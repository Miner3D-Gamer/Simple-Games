from typing import Literal, Dict, Union, Iterable, Tuple, Optional, Any, List, Callable

import tge


allowed_inputs = ["arrows", "range-{min}-{max}"]


from custom_typing import Game

import os
import importlib
from copy import deepcopy
import traceback
import sys
import time
import json

debug = True
record_input = False
current_folder = os.path.dirname(__file__)
record_directory = os.path.join(current_folder, "inputs")
games_folders = [os.path.join(current_folder, "games")]
language_folder = os.path.join(current_folder, "language")
language = "en"
timeout = 5  # seconds
user = tge.tbe.get_username()

record_file = f"{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}-inputs-"

record_path = os.path.join(record_directory, record_file)


if record_input:
    os.makedirs(record_directory, exist_ok=True)


current_language_keys: Dict[str, str] = {}


def load_language(language: str)->None:
    global current_language, current_language_keys
    requested_language_file = os.path.join(language_folder, f"{language}.json")
    if not os.path.exists(requested_language_file):
        raise ValueError(f"Language {language} not found ({requested_language_file})")
    with open(requested_language_file, "r", encoding="utf-8") as f:
        language_file: Dict[Literal["keys", "language"], Union[Dict[str, str], List[str]]] = json.load(f)
        keys = language_file.get("keys", None)
        if keys is None:
            return
        current_language = language
        current_language_keys = keys # type: ignore


def get_localization(key: str, *inserts, error_on_insufficient_arguments: bool = False) -> str:
    string:str = current_language_keys.get(key, key)
    amount = string.count("%s")
    expected = len(inserts)
    if not expected == amount:
        if error_on_insufficient_arguments:
            raise ValueError("Insufficient arguments")
        return string + " <-> " +get_localization("insufficient_arguments", error_on_insufficient_arguments=True) + " %s/%s" % (expected, amount)
    return string % tuple(inserts)


def request_input() -> str:
    try:
        inp = input()
    except ValueError:
        inp = ""
    except KeyboardInterrupt:
        send(get_localization("input.force_close"))
        quit()

    return inp


def log(*msg:Any):
    print(*msg)


def send(msg: str):
    tge.console.clear()
    print(msg)


def error_message(msg: str):
    log(msg)
    # send(msg)


GAMES: Dict[str, Any] = {"games": {}}


def add_input_to_list(input: str, current_game: str):
    with open(
        os.path.join(record_path + current_game + ".txt"), "a", encoding="utf-8"
    ) as f:
        f.write(f"{input}\n")


def load_inputs(inputs: Union[str, List[str], Tuple[str]]) -> Tuple[List[str], str]:
    if isinstance(inputs, tuple):
        new_inputs: List[str] = []
        for input in inputs:
            internal_inputs, err = load_inputs(input)
            if err:
                return [], err
            new_inputs.extend(internal_inputs)

        return new_inputs, ""
    if isinstance(inputs, str):
        if inputs.startswith("range-"):
            inputs = inputs[6:].split("-", 1)
            if not (inputs[0].isdigit() or inputs[1].isdigit()):
                return [], "Expected number in number range but got: %s-%s" % inputs
            inputs = [str(x) for x in [*range(int(inputs[0]), int(inputs[1]) + 1)]]
        else:
            got_it = False
            match inputs:
                case "arrows":
                    inputs = [*"⬅⬆⬇➡"]
                    got_it = True
                case _:
                    raise BaseException("Hi, please report me. Dev forgot to test me")
            if not got_it:
                raise ValueError("Invalid input preset")
    elif not tge.tbe.is_iterable(inputs):
        return [], "Inputs are not iterable"

    if isinstance(inputs, str):
        return [], "Invalid input preset"
    
    return inputs, ""


def load_game(game:Game) -> Union[str, None]:
    # Init given game instance
    thing = game() # type: ignore
    
    try:
        game_result = tge.function_utils.run_function_with_timeout(thing.setup, timeout, {"user": user, "interface": "console"})
    except BaseException as e:
        return "Error occurred while trying to load game: %s %s" % (
            e,
            traceback.format_exc(),
        )
    if game_result is tge.function_utils.TimeoutResult:
        return "Error: Setup timeout"
    if not hasattr(thing, "info"):
        return "Error: Missing game info -> info()"
    if not hasattr(thing, "main"):
        return "Error: Missing game mainloop -> main()"
    if not hasattr(thing, "setup"):
        return "Error: Missing game setup -> setup()"
    try:
        info: Union[Any, Dict[Literal["name", "id", "inputs"], str]] = tge.function_utils.run_function_with_timeout(thing.info, timeout)
    except BaseException as e:
        return "Error occurred while trying to receive info from game: %s" % e
    if info is tge.function_utils.TimeoutResult:
        return "Error: Info timeout"
    if not isinstance(info, dict):
        return "Invalid info typing: %s" % type(info)
    
    name = info.get("name", "")
    id = info.get("id", "")
    inputs = info.get("inputs", "")

    if isinstance(inputs, str):
        if inputs:
            inputs, errors = load_inputs(inputs)
            if errors:
                return errors
    else:
        return "Invalid type of initial inputs received"

    if isinstance(id, str):
        if not id:
            return "Id cannot be empty"
    else:
        return "Invalid id type"

    if isinstance(name, str):
        if not name:
            return "Name cannot be empty"
    else:
        return "Invalid name type"

    global GAMES
    GAMES["games"][id] = {}
    GAMES["games"][id]["game"] = thing
    GAMES["games"][id]["inputs"] = inputs
    GAMES["games"][id]["name"] = name


for game_folder in games_folders:
    sys.path.append(game_folder)
    for root, dirs, files in os.walk(game_folder, topdown=False):
        if root == game_folder:
            for dir in dirs:
                # dir = os.path.join(root, dir)
                try:
                    game = importlib.import_module(dir)
                    if not hasattr(game, "Game"):
                        log("Module %s missing game" % dir)
                        continue
                except TypeError:
                    continue
                except BaseException as e:
                    log("Error while importing %s: %s" % (dir, e))
                    continue
                if not isinstance(game.Game, Callable):
                    log("Module %s missing game" % dir)
                error = load_game(game.Game) # type: ignore

                if error:
                    traceback.print_exc()
                    log("Error importing %s:\n%s" % (dir, error))
            else:
                break


def redirect_key(key: str):
    key_translator = {
        "w": "⬆",
        "a": "⬅",
        "s": "⬇",
        "d": "➡",
    }
    return key_translator.get(key, key)


def run_game(
    game: Game, game_id: str, frame: str, accepted_inputs: List[str], give_old_frame: bool
):
    send_new_frame = True
    # last_frame = ""
    end, start = 0, 0
    while True:
        old_frame = ""
        if send_new_frame:
            send(frame + "\nValid inputs: %s" % accepted_inputs)
            send_new_frame = False
            log(get_localization("game.debug.frame_time") % (end - start) + "\n")

        user_input = request_input()
        if user_input.startswith("& "):
            quit()
        original_user_input = user_input
        tge.console.clear_lines(user_input.count("\n") + 1)
        if len(user_input) != 1 or not user_input:
            continue
        if user_input in accepted_inputs:
            input_id = accepted_inputs.index(user_input)
        else:
            user_input = redirect_key(user_input)
            if user_input in accepted_inputs:
                input_id = accepted_inputs.index(user_input)
            else:
                continue
        if record_input:
            add_input_to_list(original_user_input, game_id)
        start = time.time()

        inputs: List[Union[str, int]] = [input_id, user] + ([old_frame] if give_old_frame else [])
        
        try:
            output = tge.function_utils.run_function_with_timeout(game.main, timeout, *inputs)
            # output = game.main(input_id, user)
        except SystemExit:
            break
        except KeyboardInterrupt:
            error_message(get_localization("exit.keyboard_interrupt"))
            request_input()
            break
        except BaseException as e:
            error_message(
                "\n"+ get_localization("game.exception.unhandled")% (e, traceback.format_exc())
            )

            request_input()
            break
        finally:
            end = time.time()

        if output is tge.function_utils.TimeoutResult:
            error_message("\nMain function timed out")
            request_input()
            break

        if output is None:
            error_message("\nAn error has occurred. More is not known")
            request_input()
            break

        if output:
            if not isinstance(output, dict):
                error_message("\nInvalid return type: %s" % type(output))
                request_input()
                break
            action = output.get("action", "")
            new_frame = output.get("frame", "")
            if isinstance(new_frame, str) and new_frame != "":
                if frame != new_frame:
                    old_frame = frame
                    frame = new_frame
                    send_new_frame = True
            if isinstance(action, str) and action != "":
                if action == "end":
                    if old_frame != new_frame:
                        send(frame)
                    request_input()
                    break
                if action == "change_inputs":
                    requested_inputs = output.get("inputs", "")
                    if requested_inputs != "":
                        accepted_inputs, errors = load_inputs(requested_inputs)

                        if errors:
                            error_message(
                                "\nReceived invalid input request when application tried changing inputs: %s"
                                % errors
                            )
                            request_input()
                            break


def select_game(game_id: str) -> Union[Tuple[str, List[str], Game, bool], Literal[""]]:
    global GAMES
    game: Game = deepcopy(GAMES["games"][game_id]["game"])
    
    try:
        result = tge.function_utils.run_function_with_timeout(
            game.setup, timeout, info={"user": user, "interface": "console"}
        )
    except BaseException as e:
        error_message(
            "Error while receiving initial frame from game: %s %s"
            % (e, traceback.format_exc())
        )
        request_input()
        return ""
    if isinstance(result, tge.function_utils.TimeoutResult):
        error_message("Timeout while setup")
        request_input()
        return ""
    things = len(result)
    if things == 3:
        frame, requested_inputs, settings = result
    elif things == 2:
        frame, requested_inputs = result
        settings = {}
    else:
        return ""

    accepted_inputs, errors = load_inputs(requested_inputs)
    if errors:
        error_message(
            "Received invalid input request while trying to load game: %s" % errors
        )
        request_input()
        return ""
    return frame, accepted_inputs, game, bool(settings.get("receive_last_frame", False))


def select_game_from_user(user: str):
    while True:
        log("Selected Username:", user)
        game_amount = len(GAMES["games"])
        if game_amount == 1:
            game_id = [*GAMES["games"]][0]
            break
        if game_amount == 0:
            send("No games available")
            quit()
        print_string = get_localization("game_selection.game_list")
        for game in GAMES["games"]:
            
            print_string += "\n"+get_localization("game_selection.individual_game", GAMES["games"][game]["name"], game)
        print_string += "\n"
        send(print_string)
        game = request_input()
        if not game:
            continue
        if game[0] == "&":
            quit()
        game_id = tge.tbe.strict_autocomplete(game, GAMES["games"])
        if not isinstance(game_id, str):
            tge.console.clear()
            continue
        break
    return game_id


load_language(language)




while True:
    game_id = select_game_from_user(user)
    
    tge.console.clear()
    stuff = select_game(game_id)
    if stuff == "":
        continue
    first_frame, inputs, game, give_old_frame = stuff
    run_game(game, game_id, first_frame, inputs, give_old_frame)
