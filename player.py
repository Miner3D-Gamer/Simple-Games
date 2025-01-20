from typing import (
    Literal,
    Dict,
    Union,
    Tuple,
    Optional,
    Any,
    List,
    Callable,
    TypeAlias,
)
from collections.abc import Callable as abc_Callable

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

# cu: change_user # Change user mid-game
# fq: force_quit  # Force exit current game
# fi: force_input # Input invalid/unaccounted character for current game (There is a high chance the game will crash if this is used, only use if necessary)

commands = {
    "cu": {"description": "Change user mid-game", "function": None, "args": ["str"]},
    "fq": {"description": "Force quit", "function": None, "args": 0},
    "fi": {"description": "Force input", "function": None, "args": ["int"]},
}

debug = True
record_input = False
current_folder = os.path.dirname(__file__)
record_directory = os.path.join(current_folder, "inputs")
games_folders = [os.path.join(current_folder, "games")]
language_folder = os.path.join(current_folder, "language")
language = "en"
timeout = 5  # seconds
user = tge.tbe.get_username()
current_language = ""

from lib import wait_for_key

record_file = f"{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}-inputs-"

record_path = os.path.join(record_directory, record_file)

tbh = "⠀⠀⠀⠀⠀⠀⢀⣠⠤⠔⠒⠒⠒⠒⠒⠢⠤⢤⣀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⠴⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠲⣄⠀⠀⠀\n⠀⠀⡰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⠀\n⠀⡸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀\n⠀⡇⠀⠀⠀⢀⡶⠛⣿⣷⡄⠀⠀⠀⣰⣿⠛⢿⣷⡄⠀⠀⠀⢸⠀\n⠀⡇⠀⠀⠀⢸⣷⣶⣿⣿⡇⠀⠀⠀⢻⣿⣶⣿⣿⣿⠀⠀⠀⢸⠀\n⠀⡇⠀⠀⠀⠈⠛⠻⠿⠟⠁⠀⠀⠀⠈⠛⠻⠿⠛⠁⠀⠀⠀⢸⠀\n⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠏⠀\n⠀⠀⠈⠢⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣚⡁⠀⠀\n⠀⠀⠀⠀⠈⠙⠒⢢⡤⠤⠤⠤⠤⠤⠖⠒⠒⠋⠉⠉⠀⠀⠉⠉⢦\n⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸\n⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⣤⠀⠀⠀⢀⣀⣀⣀⠀⠀⠀⢸\n⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀⢠⣿⠀⠀⠀⢸⠀⠀⣿⠀⠀⠀⣸\n⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⠀⠀⢸⠘⡆⠀⠀⢸⣀⡰⠋⣆⠀⣠⠇\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⠤⠤⠼⠀⠘⠤⠴⠃⠀⠀⠀⠈⠉⠁⠀"


def pad_value(val: Any, how_many: int, char: str) -> str:
    return str(val).rjust(how_many, char)


def get_time_stamp() -> str:
    now = time.localtime()
    return (
        f"{now.tm_year}"
        + "-"
        + pad_value(now.tm_mon, 2, "0")
        + "-"
        + pad_value(now.tm_mday, 2, "0")
        + "-"
        + pad_value(now.tm_hour, 2, "0")
        + ":"
        + pad_value(now.tm_min, 2, "0")
        + ":"
        + pad_value(now.tm_sec, 2, "0")
    )


if record_input:
    os.makedirs(record_directory, exist_ok=True)


current_language_keys: Dict[str, str] = {}
GAMES: Dict[str, Any] = {"games": {}}


def load_language(language: str) -> None:
    global current_language, current_language_keys
    requested_language_file = os.path.join(language_folder, f"{language}.json")
    if not os.path.exists(requested_language_file):
        raise ValueError(f"Language {language} not found ({requested_language_file})")
    with open(requested_language_file, "r", encoding="utf-8") as f:
        language_file: Dict[
            Literal["keys", "language"], Union[Dict[str, str], List[str]]
        ] = json.load(f)
        keys = language_file.get("keys", None)
        if keys is None:
            return
        current_language = language
        current_language_keys = keys  # type: ignore


def get_localization(key: str, *inserts) -> str:
    empty_string_key = "engine.translation.empty_translation"
    insufficient_arguments_key = "engine.translation.insufficient_arguments"

    string: str = current_language_keys.get(key, key)

    # If the string corresponding to the inputted key is empty, try to get a fallback key. If that fails, it just errors
    if string == "":
        if key == empty_string_key:
            ValueError("Empty string for key")
        string = get_localization(empty_string_key)

    translation_key_insert_amount = string.count("%s")
    given_key_insert_amount = len(inserts)

    # If the given key insert amount is not equal to the translation key insert amount, try to get a fallback key and if the fallback key is also faulty, error
    if given_key_insert_amount != translation_key_insert_amount:

        if key == insufficient_arguments_key:
            raise ValueError("Insufficient arguments")
        return "'%s' <-> %s %s!=%s" % (
            string,
            get_localization(insufficient_arguments_key),
            given_key_insert_amount,
            translation_key_insert_amount,
        )
    return string % tuple(inserts)


class ALL_FINE: ...


class INFO: ...


class DEBUG: ...


class WARNING: ...


class ERROR: ...


class FATAL_ERROR: ...


LOGGING_ANNOTATION: TypeAlias = (
    type[ALL_FINE]
    | type[INFO]
    | type[WARNING]
    | type[DEBUG]
    | type[ERROR]
    | type[FATAL_ERROR]
)


def request_input(single_letter=True) -> str:
    total = ""
    try:
        while True:
            inp = wait_for_key()
            if not single_letter:
                print(inp, end="", flush=True)
            else:
                total += inp
                break

            if inp in "\r\n":
                break
            else:
                total += inp
    except ValueError:
        total = ""
    except KeyboardInterrupt:
        send(get_localization("engine.input.force_close"))
        quit()
    return total


def console_log(*msg: Any):
    print(*msg)


def send(msg: str) -> dict[LOGGING_ANNOTATION, str]:
    # ANSI escape sequence to move cursor to top-left corner
    CURSOR_UP = "\033[H"
    # ANSI escape sequence to clear from cursor to end of screen
    CLEAR_FROM_CURSOR = "\033[J"

    print(f"{CURSOR_UP}{CLEAR_FROM_CURSOR}{msg}", end="", flush=True)

    return {}


def log(msg: str, logging: LOGGING_ANNOTATION = ALL_FINE) -> bool:
    if logging is ALL_FINE:
        console_log(msg)
        return False
    if logging is INFO:
        console_log("[%s] INFO> %s" % (get_time_stamp(), msg))
        return False
    if logging is WARNING:
        console_log("[%s] WARNING> %s" % (get_time_stamp(), msg))
        return False
    if logging is DEBUG:
        console_log("[%s] DEBUG> %s" % (get_time_stamp(), msg))
        return False
    if logging is ERROR:
        console_log("[%s] ERROR> %s" % (get_time_stamp(), msg))
        return False
    if logging is FATAL_ERROR:
        console_log("[%s] FATAL_ERROR> %s" % (get_time_stamp(), msg))
        return True

    log("Unknown logging type: %s for '%s'" % (logging, msg), ERROR)
    return False


def add_input_to_list(key_input: str, current_game: str):
    with open(
        os.path.join(record_path + current_game + ".txt"), "a", encoding="utf-8"
    ) as f:
        f.write(f"{key_input}\n")


def load_inputs(inputs: Union[str, List[str], Tuple[str]]) -> Tuple[List[str], str]:
    if isinstance(inputs, tuple):
        new_inputs: List[str] = []
        for key_input in inputs:
            internal_inputs, err = load_inputs(key_input)
            if err:
                return [], err
            new_inputs.extend(internal_inputs)

        return new_inputs, ""
    elif isinstance(inputs, str):
        if inputs.__contains__("-"):
            if inputs[0].isdigit() or inputs.startswith("range-"):
                if inputs.startswith("range-"):
                    inputs = inputs[6:]
                inputs = inputs.split("-", 1)
                if len(inputs) != 2:
                    return (
                        [],
                        "Expected number in number range (num1-num2) but got: %s"
                        % inputs,
                    )

                if not (inputs[0].isdigit() or inputs[1].isdigit()):
                    return [], "Expected number in number range but got: %s-%s" % inputs

                def try_convert(x):
                    try:
                        return int(x)
                    except ValueError:
                        return (x,)

                start = try_convert(inputs[0])
                if not isinstance(start, int):
                    return (
                        [],
                        "First value in input number range is not a number: %s" % start,
                    )

                end = try_convert(inputs[1])
                if not isinstance(end, int):
                    return (
                        [],
                        "Second value in input number range is not a number: %s" % end,
                    )

                if 0 > start or start > 9:
                    return (
                        [],
                        "First value in input number range is not between 0 and 9: %s"
                        % start,
                    )

                if 0 > end or end > 9:
                    return (
                        [],
                        "Second value in input number range is not between 0 and 9: %s"
                        % end,
                    )

                inputs = [
                    str(x) for x in [*range(start, end + 1, 1 if start < end else -1)]
                ]
            else:
                return [], "Expected number in number range but got: %s" % inputs
        else:
            got_it = True
            match inputs:
                case "arrows":
                    inputs = [*"⬅⬆⬇➡"]

                case _:
                    got_it = False
                    # raise BaseException("Hi, please report me. Dev forgot to test me \n%s"%tbh)

            if not got_it:
                raise ValueError("Invalid input preset")
    elif isinstance(inputs, dict):
        presets: str | list[str] = inputs.get("presets", [])
        custom: list[str] = inputs.get("custom", [])
        if not tge.tbe.is_iterable(presets):
            return [], "Preset is not iterable"
        
        if not tge.tbe.is_iterable(custom):
            return [], "Custom is not iterable"
        
        preset_inputs = load_inputs(presets)
        if preset_inputs[1]:
            return [], preset_inputs[1]

        custom_inputs = load_inputs(custom)
        if custom_inputs[1]:
            return [], custom_inputs[1]

        return preset_inputs[0] + custom_inputs[0], ""

    elif not tge.tbe.is_iterable(inputs):
        return [], "Inputs are not iterable"

    if isinstance(inputs, str):
        return [], "Invalid input preset"

    return inputs, ""


def load_game(game: Game) -> Union[str, None]:
    # Init given game instance
    thing = game()  # type: ignore

    try:
        game_result = tge.function_utils.run_function_with_timeout(
            thing.setup, timeout, {"user": user, "interface": "console"}
        )
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
        info: Union[Any, Dict[Literal["name", "id", "inputs"], str]] = (
            tge.function_utils.run_function_with_timeout(thing.info, timeout)
        )
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
    return None

all_error = []

for game_folder in games_folders:
    sys.path.append(game_folder)
    for root, dirs, files in os.walk(game_folder, topdown=False):
        if root == game_folder:
            for dir in dirs:
                # dir = os.path.join(root, dir)
                try:
                    game = importlib.import_module(dir)
                    if not hasattr(game, "Game"):
                        all_error.append("Module %s missing game" % dir)
                        continue
                except TypeError:
                    continue
                except BaseException as e:
                    all_error.append("Error while importing %s: %s" % (dir, e))
                    continue
                if not callable(game.Game):
                    all_error.append("Module %s missing game" % dir)
                error = load_game(game.Game)  # type: ignore

                if error:
                    traceback.print_exc()
                    all_error.append("Error importing %s:\n%s" % (dir, error))
            else:
                break
if all_error:
    for e in all_error:
        log(e, ERROR)
    request_input()

def redirect_key(key: str):
    key_translator = {
        "w": "⬆",
        "a": "⬅",
        "s": "⬇",
        "d": "➡",
        "UP": "⬆",
        "LEFT": "⬅",
        "DOWN": "⬇",
        "RIGHT": "➡",
    }
    return key_translator.get(key, key)


def run_game(
    game: Game,
    game_id: str,
    frame: str,
    accepted_inputs: List[str],
    give_old_frame: bool,
):
    send_new_frame = True
    debug_mode_enabled = True
    end, start = 0.0, 0.0
    while True:
        old_frame = ""
        if send_new_frame:
            send_new_frame = False
            if debug_mode_enabled:
                send(frame + "\nValid inputs: %s\n" % accepted_inputs)
                log(
                    get_localization("engine.debug.frame_time", (end - start)) + "\n",
                    DEBUG,
                )

        user_input = request_input(True)
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

        inputs: List[Union[str, int]] = [input_id, user] + (
            [old_frame] if give_old_frame else []
        )

        try:
            output = tge.function_utils.run_function_with_timeout(
                game.main, timeout, *inputs
            )
            # output = game.main(input_id, user)
        except SystemExit:
            break
        except KeyboardInterrupt:
            log(get_localization("exit.keyboard_interrupt"))
            request_input()
            break
        except BaseException as e:
            log(
                "\n"
                + get_localization(
                    "engine.game.exception.unhandled", e, traceback.format_exc()
                )
            )

            request_input()
            break
        finally:
            end = time.time()

        if output is tge.function_utils.TimeoutResult:
            log("\nMain function timed out")
            request_input()
            break

        if output is None:
            log("\n" + get_localization("engine.game.error.unhandled"))
            request_input()
            break

        if output:
            if not isinstance(output, dict):
                log(
                    "\n"
                    + get_localization(
                        "engine.game.error.invalid_return_type", type(output)
                    )
                )
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
                            log(
                                "\nReceived invalid input request when application tried changing inputs: %s"
                                % errors
                            )
                            request_input()
                            break


def select_game(game_id: str) -> Union[Tuple[str, List[str], Game, bool], str]:
    global GAMES
    game: Game = deepcopy(GAMES["games"][game_id]["game"])

    try:
        result = tge.function_utils.run_function_with_timeout(
            game.setup, timeout, info={"user": user, "interface": "console"}
        )
    except BaseException as e:
        return "Error while receiving initial frame from game: %s %s" % (
            e,
            traceback.format_exc(),
        )
    if isinstance(result, tge.function_utils.TimeoutResult):
        return "Timeout while setup, took over %s seconds" % timeout
    game_return_amount = len(result)
    if game_return_amount == 3:
        frame, requested_inputs, settings = result
    elif game_return_amount == 2:
        frame, requested_inputs = result
        settings = {}
    else:
        return (
            "Invalid amount of return values returned, expected 2 or 3 but got %s"
            % game_return_amount
        )
    if settings is None:
        settings = {}
    if not isinstance(frame, str):
        return "Invalid frame type, expected string but got %s" % type(frame)
    if not isinstance(settings, dict):
        return "Invalid settings type, expected dict but got %s" % type(settings)

    accepted_inputs, errors = load_inputs(requested_inputs)
    if errors:
        return "Received invalid input request while trying to load game: %s" % errors
    return frame, accepted_inputs, game, bool(settings.get("receive_last_frame", False))


def select_game_from_user(user: str):
    while True:
        send_string = "Selected Username: %s\n" % user
        game_amount = len(GAMES["games"])

        # No need for the user to manually select a game if there is just a single game
        if game_amount == 1:
            game_id = [*GAMES["games"]][0]
            break

        if game_amount == 0:
            send("No games available")
            quit()

        # Store games and insert them into a game list
        game_list_string = ""
        for game in GAMES["games"]:

            game_list_string += "\n" + get_localization(
                "engine.game_selection.individual_game",
                GAMES["games"][game]["name"],
                game,
            )
        send_string += get_localization(
            "engine.game_selection.game_list", game_list_string
        )

        # Padding not needed in non console?
        send_string += "\n"
        send(send_string)

        game = request_input(False)
        if not game:
            continue

        # For quicker development
        if game[0] == "&":
            quit()

        # Autocomplete
        game_id = tge.tbe.strict_autocomplete(game, GAMES["games"])
        if not isinstance(game_id, str):
            tge.console.clear()
            continue
        break
    return game_id


def start_engine():
    while True:
        game_id = select_game_from_user(user)

        tge.console.clear()
        stuff = select_game(game_id)
        if isinstance(stuff, str):
            send(
                "Error while running .setup() of the currently selected game:\n" + stuff
            )
            request_input()
            continue
        first_frame, inputs, game, give_old_frame = stuff
        run_game(game, game_id, first_frame, inputs, give_old_frame)


load_language(language)

start_engine()
