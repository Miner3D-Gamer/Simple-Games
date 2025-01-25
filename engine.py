from typing import Literal, Dict, Union, Tuple, Optional, Any, List, Callable, Type
from wrapper.console import *

import tge


allowed_inputs = ["arrows", "range-{min}-{max}"]


from custom_typing import *

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
timeout = 3  # seconds
user = tge.tbe.get_username()
current_language = ""

# from lib import wait_for_key

record_file = f"{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}-inputs-"

record_path = os.path.join(record_directory, record_file)

tbh = "⠀⠀⠀⠀⠀⠀⢀⣠⠤⠔⠒⠒⠒⠒⠒⠢⠤⢤⣀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⠴⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠲⣄⠀⠀⠀\n⠀⠀⡰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⠀\n⠀⡸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀\n⠀⡇⠀⠀⠀⢀⡶⠛⣿⣷⡄⠀⠀⠀⣰⣿⠛⢿⣷⡄⠀⠀⠀⢸⠀\n⠀⡇⠀⠀⠀⢸⣷⣶⣿⣿⡇⠀⠀⠀⢻⣿⣶⣿⣿⣿⠀⠀⠀⢸⠀\n⠀⡇⠀⠀⠀⠈⠛⠻⠿⠟⠁⠀⠀⠀⠈⠛⠻⠿⠛⠁⠀⠀⠀⢸⠀\n⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠏⠀\n⠀⠀⠈⠢⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣚⡁⠀⠀\n⠀⠀⠀⠀⠈⠙⠒⢢⡤⠤⠤⠤⠤⠤⠖⠒⠒⠋⠉⠉⠀⠀⠉⠉⢦\n⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸\n⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⣤⠀⠀⠀⢀⣀⣀⣀⠀⠀⠀⢸\n⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀⢠⣿⠀⠀⠀⢸⠀⠀⣿⠀⠀⠀⣸\n⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⠀⠀⢸⠘⡆⠀⠀⢸⣀⡰⠋⣆⠀⣠⠇\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⠤⠤⠼⠀⠘⠤⠴⠃⠀⠀⠀⠈⠉⠁⠀"


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


# def request_input(single_letter=True) -> str:
#     total = ""
#     try:
#         while True:
#             inp = wait_for_async_function(wait_for_key, id)
#             if inp is None:
#                 raise KeyboardInterrupt("Received None from wait_for_key")
#             if not single_letter:
#                 print(inp, end="", flush=True)
#             else:
#                 total += inp
#                 break

#             if inp in "\r\n":
#                 break
#             else:
#                 total += inp
#     except ValueError:
#         total = ""
#     except KeyboardInterrupt:
#         wait_for_async_function(send, get_localization("engine.input.force_close"))
#         quit()
#     return total


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
            defaults = {"arrows": [*"⬅⬆⬇➡"]}

            inputs = defaults.get(inputs, "")
            # raise BaseException("Hi, please report me. Dev forgot to test me \n%s"%tbh)

            if inputs == "":
                raise ValueError("Invalid input preset")
    elif isinstance(inputs, dict):
        presets: Union[str, list[str]] = inputs.get("presets", [])
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


def restart_program():
    """Restarts the current program."""
    python = sys.executable
    os.execl(python, python, *sys.argv)


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


class StopEngine:
    __slots__ = ("last_frame",)

    def __init__(self, last_frame: str) -> None:
        self.last_frame = last_frame


class SelectedGame:
    __slots__ = ("name", "id")

    def __init__(self, name: str, id: str) -> None:
        self.name = name
        self.id = id

    def __repr__(self) -> str:
        return f"{self.name} ({self.id})"


class ChangeInputs:
    __slots__ = ("inputs", "frame")

    def __init__(self, inputs: List[str], frame: Optional[str]) -> None:
        self.inputs = inputs
        self.frame = frame


class Engine:
    __slots__ = (
        "game",
        "game_id",
        "first_frame",
        "frame",
        "send_new_frame",
        "accepted_inputs",
        "old_frame",
        "deltatime",
        "time_between_frame_start",
        "frame_count",
        "ready",
        "written",
        "time_between_frame",
    )

    def __init__(self) -> None:
        self.ready = False
        self.game: Game
        self.frame: str
        self.game_id: str
        self.first_frame: str
        self.frame_count: int
        self.send_new_frame: bool = True
        self.accepted_inputs: List[str]
        self.old_frame: str = ""
        self.written = ""
        self.deltatime = 0.0

    def run_game(
        self,
        user_input: str,
        user_id:str,
        username:str
    ) -> Optional[Union[Exception, str, StopEngine, ChangeInputs]]:
        if not self.ready:
            return Exception("Engine is not ready -> No game has been loaded")
        debug_mode_enabled = True
        end, start = 0.0, 0.0
        self.frame_count += 1
        if self.frame_count == 0:
            self.time_between_frame_start = time.time()
        self.time_between_frame = self.time_between_frame_start - time.time()

        if not self.send_new_frame:
            return self.old_frame

        # self.send_new_frame = False
        if self.frame_count == 0:
            return (
                self.first_frame
                + "\nValid inputs: %s\n" % self.accepted_inputs
                + (
                    get_localization("engine.debug.frame_time", (end - start)) + "\n"
                    if debug_mode_enabled
                    else ""
                )
            )

        if user_input.startswith("& "):
            quit()
        original_user_input = user_input
        # tge.console.clear_lines(user_input.count("\n") + 1)
        if len(user_input) != 1 or not user_input:
            return None
        if user_input in self.accepted_inputs:
            input_id = self.accepted_inputs.index(user_input)
        else:
            user_input = redirect_key(user_input)
            if user_input in self.accepted_inputs:
                input_id = self.accepted_inputs.index(user_input)
            else:
                return None
        # if record_input:
        #     add_input_to_list(original_user_input, self.game_id)

        start = time.time()

        try:
            output = tge.function_utils.run_function_with_timeout(
                self.game.main,
                timeout,
                input_id,
                {
                    "old_frame": self.old_frame,
                    "frame": self.frame_count,
                    "deltatime": self.deltatime,
                    "time_between_frame_start": self.time_between_frame,
                    "user_id": user_id,
                    "username": username
                },
            )
            # output = game.main(input_id, user)
        except SystemExit:
            return Exception("SystemExit")
        except KeyboardInterrupt:
            return Exception(get_localization("exit.keyboard_interrupt"))
        except BaseException as e:
            return "\n" + get_localization(
                "engine.game.exception.unhandled", e, traceback.format_exc()
            )
        finally:
            now = time.time()
            self.deltatime = now - start
            self.time_between_frame_start = now
        ###############################################
        if output is tge.function_utils.TimeoutResult:
            return Exception(get_localization("engine.game.error.timeout", timeout))

        if output is None:
            return Exception("\n" + get_localization("engine.game.error.unhandled"))

        if not isinstance(output, dict):
            return Exception(
                "\n"
                + get_localization(
                    "engine.game.error.invalid_return_type", type(output)
                )
            )
        action = output.get("action", "")
        new_frame = output.get("frame", "")
        if not isinstance(action, str):
            return Exception(
                "\n"
                + get_localization(
                    "engine.game.error.invalid_return_type.action", type(action)
                )
            )
        if not isinstance(new_frame, str):
            return Exception(
                "\n"
                + get_localization(
                    "engine.game.error.invalid_return_type.new_frame", type(new_frame)
                )
            )

        if new_frame != "":
            if self.frame != new_frame:
                self.old_frame = self.frame
                self.frame = new_frame
                self.send_new_frame = True
        if action != "":
            if action == "end":
                if self.old_frame != new_frame:
                    self.ready = False
                    return StopEngine(self.frame)
                return None
            elif action == "change_inputs":
                requested_inputs = output.get("inputs", "")
                if requested_inputs != "":
                    self.accepted_inputs, errors = load_inputs(requested_inputs)

                    if errors:
                        return Exception(
                            "\nReceived invalid input request when application tried changing inputs: %s"
                            % errors
                        )
                    return ChangeInputs(self.accepted_inputs, self.frame)
            else:
                return Exception(
                    "\n" + get_localization("engine.game.error.invalid_action", action)
                )
        return self.frame

    def get_last_frame(self) -> str:
        return self.frame

    def select_game(self, game_id: str) -> Optional[str]:
        global GAMES
        try:
            game: Game = deepcopy(GAMES["games"][game_id]["game"])
        except TypeError as e:
            return get_localization("engine.game_selection.load.error.type_error", e)

        try:
            result = tge.function_utils.run_function_with_timeout(
                game.setup, timeout, info={"user": user, "interface": "console"}
            )
        except BaseException as e:
            return get_localization(
                "engine.game_selection.load.error",
                e,
                traceback.format_exc(),
            )
        if isinstance(result, tge.function_utils.TimeoutResult):
            return get_localization("engine.game_selection.load.error.timeout", timeout)
        if not isinstance(result, (list, tuple)):
            return get_localization(
                "engine.game_selection.load.error.invalid_returns_from_setup", result
            )
        game_return_amount = len(result)
        if game_return_amount == 3:
            frame, requested_inputs, settings = result
        elif game_return_amount == 2:
            frame, requested_inputs = result
            settings = {}
        else:
            return get_localization(
                "engine.game_selection.load.error.invalid_returns_from_setup",
                game_return_amount,
            )
        if settings is None:
            settings = {}
        if not isinstance(frame, str):
            return "Invalid frame type, expected string but got %s" % type(frame)
        if not isinstance(settings, dict):
            return "Invalid settings type, expected dict but got %s" % type(settings)

        accepted_inputs, errors = load_inputs(requested_inputs)
        if errors:
            return (
                "Received invalid input request while trying to load game: %s" % errors
            )
        self.first_frame = frame
        self.frame_count = -1
        self.game = game
        self.accepted_inputs = accepted_inputs
        self.ready = True
        self.frame = ""
        self.old_frame = ""
        self.game_id = game_id
        return None

    def select_game_from_user(
        self, user: str, key: Union[str, int]
    ) -> Union[Exception, str, SelectedGame]:
        send_string = (
            get_localization("engine.game_selection.selected_name", user) + "\n"
        )
        game_amount = len(GAMES["games"])

        # No need for the user to manually select a game if there is just a single game
        if game_amount == 1:
            game_id: str = [*GAMES["games"]][0]
            self.select_game(game_id)
            return SelectedGame(GAMES["games"][game_id]["name"], game_id)

        if game_amount == 0:
            return Exception(
                get_localization("engine.game_selection.no_games_available")
            )
        if isinstance(key, str):
            if key.isdigit():
                key = int(key)
        if isinstance(key, int):
            games_based_on_selection = tge.tbe.strict_autocomplete(
                self.written, GAMES["games"]
            )
            if key >= len(games_based_on_selection):
                return Exception(
                    get_localization("engine.game_selection.no_such_game", key)
                )
            if isinstance(games_based_on_selection, str):
                games_based_on_selection = [games_based_on_selection]
            game_id = games_based_on_selection[key]
            self.select_game(game_id)
            return SelectedGame(GAMES["games"][game_id]["name"], game_id)

        SELECT_FIRST = False
        if key == "BACKSPACE":
            self.written = self.written[:-1]
        elif key == "ENTER":
            SELECT_FIRST = True
        elif key.strip() == "":
            pass
        else:
            self.written += key

        send_string += (
            get_localization("engine.game_selection.written", self.written) + "\n"
        )

        # Store games and insert them into a game list
        game_list_string = ""
        all_games = GAMES["games"]

        games_based_on_selection = tge.tbe.strict_autocomplete(self.written, all_games)

        if len(games_based_on_selection) == 0:
            send_string += get_localization(
                "engine.game_selection.no_games_found", self.written
            )
            return send_string
        if isinstance(games_based_on_selection, str):
            games_based_on_selection = [games_based_on_selection]

        if SELECT_FIRST:
            game_id = games_based_on_selection[0]
            self.select_game(game_id)
            return SelectedGame(GAMES["games"][game_id]["name"], game_id)

        for game in games_based_on_selection:

            game_list_string += "\n" + get_localization(
                "engine.game_selection.individual_game",
                GAMES["games"][game]["name"],
                game,
            )
        send_string += get_localization(
            "engine.game_selection.game_list", game_list_string
        )

        return send_string


# def start_engine():
#     global id
#     id, user = wait_for_async_function(start)

#     while True:
#         game_id = select_game_from_user(user)

#         stuff = select_game(game_id)
#         if isinstance(stuff, str):
#             wait_for_async_function(
#                 send, id, get_localization("engine.game.start.error", stuff)
#             )
#             request_input()
#             continue
#         first_frame, inputs, game, give_old_frame = stuff
#         run_game(game, game_id, first_frame, inputs, give_old_frame)


def has_callable(module, name, dir):
    if not hasattr(module, name):
        return get_localization("engine.import.error.missing_game_class", dir, name)

    if not callable(getattr(module, name)):
        return get_localization("engine.import.error.missing_game_class", dir, name)


def get_callable(dir: str) -> Tuple[str, Any]:
    try:
        game = importlib.import_module(dir)

    except TypeError:
        return get_localization("engine.import.error.type_error", dir), None
    except BaseException as e:
        return get_localization("engine.import.error.error", dir, e), None
    return "", game


def initialize_games():
    all_error = []

    for game_folder in games_folders:
        sys.path.append(game_folder)
        for root, dirs, files in os.walk(game_folder, topdown=False):
            if root == game_folder:
                for dir in dirs:
                    # dir = os.path.join(root, dir)
                    error, game = get_callable(dir)

                    error = has_callable(game, "Game", dir)
                    if error:
                        all_error.append(error)
                        continue

                    error = has_callable(game, "Requirements", dir)
                    if os.path.exists(os.path.join(root, dir, "requirements.txt")):
                        with open(os.path.join(root, dir, "requirements.txt")) as f:
                            required_modules = f.read().split("\n")

                        required_libs = []
                        for mod in required_modules:
                            if tge.library_utils.is_library_installed(mod):
                                continue
                            required_libs.append(mod)
                        if len(required_libs) != 0:
                            log(
                                get_localization(
                                    "engine.import.requirements.missing",
                                    dir,
                                    ",\n".join(
                                        [
                                            get_localization(
                                                "engine.import.requirements.missing.single",
                                                r,
                                            )
                                            for r in required_libs
                                        ]
                                    ),
                                ),
                                ERROR,
                            )
                            download = input()
                            if download == "y":
                                log(
                                    get_localization(
                                        "engine.import.requirements.installing"
                                    ),
                                    INFO,
                                )
                                returns = tge.library_utils.install_all_libraries(
                                    required_libs
                                )
                                send_string = ""
                                for errored, error in returns:
                                    if errored:
                                        send_string += error + "\n"
                                if send_string:
                                    log(
                                        get_localization(
                                            "engine.import.requirements.error",
                                            send_string,
                                        ),
                                        ERROR,
                                    )
                                else:
                                    log(
                                        get_localization(
                                            "engine.import.requirements.success"
                                        ),
                                        INFO,
                                    )
                                restart_program()

                    error = load_game(game.Game)  # type: ignore

                    if error:
                        traceback.print_exc()
                        all_error.append(
                            get_localization("engine.import.error.load", dir, error)
                        )
                else:
                    break
    if all_error:
        for e in all_error:
            log(e, ERROR)
        # input()


def is_valid_game_id(id: str):
    return id in GAMES["games"]


load_language(language)

initialize_games()

# start_engine()
