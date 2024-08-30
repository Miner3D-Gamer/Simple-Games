from typing import Literal, Dict, Union, Iterable

class Game:
    def __init__(self) -> None: ...
    def main(self, input: int, user: str) -> None | dict: ...
    def setup(
        self,
        info: Dict[
            Literal["user", "interface"], Union[str, Literal["console", "discord"]]
        ],
    ) -> tuple[str, Iterable | Literal["arrows", "range-{min}-{max}"]]: ...
    def info(self) -> Dict[Literal["name", "id", "inputs"], str]: ...


import os
import tge
import importlib
from copy import deepcopy
import traceback
import sys
import time

debug = True
record_input = True
record_directory = os.path.join(os.path.dirname(__file__), "inputs")
games_folders = [os.path.join(os.path.dirname(__file__), "games")]
language = "en"





record_file = f"{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}-inputs-"

if record_input:
    os.makedirs(record_directory, exist_ok=True)






def get_localization(key: str) -> str:
    return key


def request_input(*inp) -> str:
    if inp:
        raise NotImplementedError("Input not expected")
    try:
        inp = input()
    except ValueError:
        inp = ""
    except KeyboardInterrupt:
        log("\nForce closed the game")
        quit()

    return inp


def log(*msg):
    print(*msg)


def send(msg: str):
    tge.console.clear()
    print(msg)


def send_add(msg: str):
    send(msg)


def error_message(msg: str):
    log(msg)
    # send(msg)


GAMES = {"games": {}}

def add_input_to_list(input:str, current_game:str):
    with open(os.path.join(record_directory, record_file + current_game + ".txt"), "a", encoding="utf-8") as f:
        f.write(f"{input}\n")


def load_inputs(inputs: str | Iterable) -> tuple[list, str]:
    if isinstance(inputs, str):
        if inputs.startswith("range-"):
            inputs = inputs[6:].split("-")
            inputs = [str(x) for x in [*range(int(inputs[0]), int(inputs[1]) + 1)]]
        else:
            match inputs:
                case "arrows":

                    inputs = [*"⬅⬆⬇➡"]
    elif not tge.tbe.is_iterable(inputs):
        return [], "Inputs are not iterable"

    if isinstance(inputs, str):
        return [], "Invalid input preset"
    return inputs, ""


def load_game(game: Game):
    try:
        game = game()
    except BaseException as e:
        return "Error occurred while trying to load game: %s %s" % (
            e,
            traceback.format_exc(),
        )

    if not hasattr(game, "info"):
        return "Error: Missing game info -> info()"
    if not hasattr(game, "main"):
        return "Error: Missing game mainloop -> main()"
    if not hasattr(game, "setup"):
        return "Error: Missing game setup -> setup()"
    try:
        info = game.info()
    except BaseException as e:
        return "Error occurred while trying to receive info from game: %s" % e
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
    GAMES["games"][id]["game"] = game
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

                error = load_game(game.Game)

                if error:
                    log("Error importing %s:\n%s" % (dir, error), traceback.print_exc())
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


user = tge.file_operations.get_appdata_path()[9:-8]
log("Selected Username:", user)
while True:
    while True:
        game_amount = len(GAMES["games"])
        if game_amount == 1:
            game_id = [*GAMES["games"]][0]
            break
        if game_amount == 0:
            log("No games available")
            quit()
        print_string = "Select game from this list:"
        print_string += "\n".join(*GAMES["games"])
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
    tge.console.clear()
    game: Game = deepcopy(GAMES["games"][game_id]["game"])
    try:
        frame, requested_inputs = game.setup({"user": user, "interface": "console"})
    except BaseException as e:
        error_message(
            "Error while receiving initial frame from game: %s %s"
            % (e, traceback.format_exc())
        )
        request_input()
        continue
    accepted_inputs, errors = load_inputs(requested_inputs)
    if errors:
        error_message(
            "Received invalid input request while trying to load game: %s" % errors
        )
        request_input()
        continue
    send_new_frame = True
    while True:
        if send_new_frame:
            send(frame)
            send_new_frame = False

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
        try:
            output = game.main(input_id, user)
        except SystemExit:
            break
        except KeyboardInterrupt:
            error_message("\nForce closed the game")
            request_input()
            break
        except BaseException as e:
            error_message(
                "\nAn error has occurred; %s \n%s" % (e, traceback.format_exc())
            )

            request_input()
            break
        finally:
            end = time.time()
            print("Game took %s seconds to generate output" % (end - start))

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
                frame = new_frame
                send_new_frame = True
            if isinstance(action, str) and action != "":
                if action == "end":
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
