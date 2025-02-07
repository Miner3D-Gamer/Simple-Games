# For maximum compatibility
# pip install pyyaml json5 tomli python-hcl2 pyhocon, hjson


import os
from typing import Literal, Dict, Union, Tuple, Optional, Any, List, Callable
from custom_typing import *
from wrapper.other import *

###### PATHS ######

current_folder = os.path.dirname(__file__)
default_record_directory = os.path.join(current_folder, "inputs")
default_games_folders = [os.path.join(current_folder, "games")]
default_language_folder = os.path.join(current_folder, "language")
default_plugin_folder = os.path.join(current_folder, "plugins")
default_cache_folder = os.path.join(current_folder, "cache")


##### PLUGINS #####

RecursiceModuleType: TypeAlias = List[Union[str, Dict[str, "RecursiceModuleType"]]]


class FrameworkContents(TypedDict):
    redirects: Dict[Literal["keys", "special"], Dict[str, str]]
    allowed_inputs: List[str]
    input_presets: List[Preset]
    allowed_modules: RecursiceModuleType
    blocked_functions: Dict[str, List[str]]


LOADED = FrameworkContents(
    redirects={"keys": {}, "special": {}},
    allowed_inputs=[],
    input_presets=[],
    allowed_modules=[],
    blocked_functions={},
)


def load_redirects(content):
    LOADED["redirects"].update(content)


def update_inputs(content):

    custom = content.get("custom", [])
    if isinstance(custom, str):
        LOADED["allowed_inputs"].extend(list(custom))
    elif isinstance(custom, list):
        LOADED["allowed_inputs"].extend(custom)
    else:
        raise Exception("Invalid custom inputs")

    presets = content.get("presets", [])
    LOADED["input_presets"].extend(presets)


def update_allowed_modules(content):
    LOADED["allowed_modules"].extend(content.get("allowed"))
    LOADED["blocked_functions"].update(content.get("disabled"))


def load_plugin(path: str):
    redirect_keys = file_config_content(path, "redirect_keys")
    if redirect_keys is not None:
        load_redirects(redirect_keys)
    load_inputs = file_config_content(path, "load_inputs")
    if load_inputs is not None:
        update_inputs(load_inputs)
    load_allowed_modules = file_config_content(path, "modules")
    if load_allowed_modules is not None:
        update_allowed_modules(load_allowed_modules)


def reload_plugins(plugin_folder):
    all_plugin_folders = os.listdir(plugin_folder)
    for plugin_folders in all_plugin_folders:
        load_plugin(os.path.join(plugin_folder, plugin_folders))


##### Import patcher needs to be the first thing that get's loaded so it can do it's job as intented
import wrapper.import_patcher as import_patcher

reload_plugins(default_plugin_folder)

import_patcher.block_modules(LOADED["blocked_functions"])


##### Start of Framework #####


from wrapper.console import *
from wrapper.shared import get_only_item_in_dict

import tge


from copy import deepcopy
import traceback
import sys
import time
import json
import re
import shutil
import ast
import importlib.util as import_util


debug = True
record_input = False
language = "en"
default_timeout = 3  # seconds
current_language = ""
default_max_actions = 128


record_file = f"{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}-inputs-"

record_path = os.path.join(default_record_directory, record_file)

tbh = "⠀⠀⠀⠀⠀⠀⢀⣠⠤⠔⠒⠒⠒⠒⠒⠢⠤⢤⣀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⢀⠴⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠲⣄⠀⠀⠀\n⠀⠀⡰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⠀\n⠀⡸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀\n⠀⡇⠀⠀⠀⢀⡶⠛⣿⣷⡄⠀⠀⠀⣰⣿⠛⢿⣷⡄⠀⠀⠀⢸⠀\n⠀⡇⠀⠀⠀⢸⣷⣶⣿⣿⡇⠀⠀⠀⢻⣿⣶⣿⣿⣿⠀⠀⠀⢸⠀\n⠀⡇⠀⠀⠀⠈⠛⠻⠿⠟⠁⠀⠀⠀⠈⠛⠻⠿⠛⠁⠀⠀⠀⢸⠀\n⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠏⠀\n⠀⠀⠈⠢⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣚⡁⠀⠀\n⠀⠀⠀⠀⠈⠙⠒⢢⡤⠤⠤⠤⠤⠤⠖⠒⠒⠋⠉⠉⠀⠀⠉⠉⢦\n⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸\n⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⣤⠀⠀⠀⢀⣀⣀⣀⠀⠀⠀⢸\n⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀⢠⣿⠀⠀⠀⢸⠀⠀⣿⠀⠀⠀⣸\n⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⠀⠀⢸⠘⡆⠀⠀⢸⣀⡰⠋⣆⠀⣠⠇\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⠤⠤⠼⠀⠘⠤⠴⠃⠀⠀⠀⠈⠉⠁⠀"


def clear_cache():
    if os.path.exists(default_cache_folder):
        shutil.rmtree(default_cache_folder)

    os.mkdir(default_cache_folder)


clear_cache()
unsafe_keywords = ["print", "eval", "exec", "open", "input"]


if record_input:
    os.makedirs(default_record_directory, exist_ok=True)


current_language_keys: Dict[str, str] = {}
GAMES: Dict[str, Any] = {"games": {}}


def load_language(language: str) -> None:
    global current_language, current_language_keys
    requested_language_file = file_config_content(default_language_folder, language)
    if requested_language_file is None:
        raise ValueError(f"Language {language} not found in {default_language_folder}")

    language_file = requested_language_file
    assert isinstance(language_file, dict)
    keys = language_file.get("keys", None)
    if keys is None:
        return
    if not isinstance(keys, dict):
        raise ValueError("Invalid language file")
    current_language = language
    current_language_keys = keys


def get_localization(key: str, *inserts) -> str:
    empty_string_key = "framework.translation.empty_translation"
    insufficient_arguments_key = "framework.translation.insufficient_arguments"

    string: str = current_language_keys.get(key, key)

    # If the string corresponding to the inputted key is empty, try to get a fallback key. If that fails, just error
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
        return "(%s) '%s' <-> %s %s!=%s" % (
            key,
            string,
            get_localization(insufficient_arguments_key),
            given_key_insert_amount,
            translation_key_insert_amount,
        )
    return string % tuple(inserts)


def add_input_to_list(key_input: str, current_game: str):
    with open(
        os.path.join(record_path + current_game + ".txt"), "a", encoding="utf-8"
    ) as f:
        f.write(f"{key_input}\n")


def load_inputs(inputs: INPUTS) -> Tuple[List[str], str]:
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
            if inputs[0].isdigit() or inputs.startswith("range"):
                if inputs.startswith("range"):
                    inputs = inputs[6:]
                inputs = inputs.strip("()")
                inputs = inputs.split("-", 1)
                if len(inputs) != 2:
                    return (
                        [],
                        get_localization(
                            "framework.load_input.error.invalid_number_range", inputs
                        ),
                    )

                if not (inputs[0].isdigit() or inputs[1].isdigit()):
                    return [], get_localization(
                        "framework.load_input.error.not_numbers", inputs
                    )

                def convert(x: str, which: str) -> Union[str, int]:
                    val = try_convert(x)
                    w = (
                        get_localization("framework.load_input.error.first")
                        if which == "first"
                        else get_localization("framework.load_input.error.second")
                    )
                    if not isinstance(val, int):
                        return get_localization(
                            "framework.load_input.error.value_not_number", w, val
                        )
                    if 0 > val or val > 9:
                        return get_localization(
                            "framework.load_input.error.value_out_of_range", w, val
                        )
                    return val

                def try_convert(x):
                    try:
                        return int(x)
                    except ValueError:
                        return (x,)

                start = convert(inputs[0], "first")

                end = convert(inputs[1], "second")

                if isinstance(start, str):
                    return [], start
                if isinstance(end, str):
                    return [], end

                inputs = [
                    str(x) for x in [*range(start, end + 1, 1 if start < end else -1)]
                ]
            else:
                return [], get_localization(
                    "framework.load_input.error.expected_number_range", inputs
                )
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
            return [], "Custom input is not iterable"

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

    inv = []
    for inp in inputs:
        if not inp in LOADED["allowed_inputs"]:
            inv.append(inp)
    if len(inv) > 0:
        return [], "Invalid inputs: %s" % inv

    return inputs, ""


def add_game_to_game_list(game: Game, interface: str):
    return_values = load_game(game, interface)
    if isinstance(return_values, str):
        return return_values

    global GAMES
    GAMES["games"][return_values[3]] = {}
    GAMES["games"][return_values[3]]["game"] = return_values[0]
    GAMES["games"][return_values[3]]["description"] = return_values[1]
    GAMES["games"][return_values[3]]["name"] = return_values[2]


def load_game(game: Game, interface: str) -> Union[str, Tuple[Game, str, str, str]]:
    # Init given game instance
    thing: Game = game()

    try:
        game_result = tge.function_utils.run_function_with_timeout(
            thing.setup, default_timeout, {"user": "", "interface": interface}
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
        info: Union[Any, Dict[Literal["name", "id", "description"], str]] = (
            tge.function_utils.run_function_with_timeout(thing.info, default_timeout)
        )
    except BaseException as e:
        return "Error occurred while trying to receive info from game: %s" % e
    if info is tge.function_utils.TimeoutResult:
        return "Error: Info timeout"
    if not isinstance(info, dict):
        return "Invalid info typing: %s" % type(info)

    name = info.get("name", "")
    id = info.get("id", "")
    description = info.get("description", "")

    if isinstance(description, str):
        if not description:
            description = "No description"
    else:
        return "Invalid description type received"

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

    return thing, description, name, id


def restart_program():
    """Restarts the current program."""
    python = sys.executable
    os.execl(python, python, *sys.argv)


def redirect_key(key: str) -> str:
    thing = LOADED["redirects"]["keys"].get(key, None)
    if thing is None:
        return key

    return LOADED["redirects"]["special"].get(thing, key)


class StopFramework(Exception):
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


class SafeFileAccess:
    def __init__(self, game_paths: list[str]) -> None:
        self.game_paths = game_paths

    def get_path_of_game(self, game_id) -> Optional[str]:
        for path in self.game_paths:
            x = os.path.join(path, game_id)
            if os.path.exists(x):
                return x
        return None

    def is_path_safe(self, path: str):
        if ".." in path:
            return False
        return True

    def get_contained_paths(self, game_id: str, path: str):
        if not self.is_path_safe(path):
            return None
        game_path = self.get_path_of_game(game_id)
        if game_path is None:
            return None
        return os.path.join(game_path, path)

    def does_file_exist(self, game_id: str, path: str) -> Optional[bool]:
        given_path = self.get_contained_paths(game_id, path)
        if given_path is None:
            return None
        return os.path.exists(given_path)

    def write_to_file(self, game_id, path: str, content: str) -> Optional[bool]:
        given_path = self.get_contained_paths(game_id, path)
        if given_path is None:
            return None
        if os.path.exists(given_path) and os.path.isfile(given_path):
            write_to_file(given_path, content)
            return True
        return False

    def get_file_contents(self, game_id: str, path: str) -> Optional[str]:
        new_path = self.get_contained_paths(game_id, path)
        if new_path is None:
            return None
        if os.path.exists(new_path) and os.path.isfile(new_path):
            return get_file_contents(new_path)

    def get_files_in_folder(self, game_id: str, path: str) -> Optional[List[str]]:
        new_path = self.get_contained_paths(game_id, path)
        if new_path is None:
            return None
        if os.path.exists(new_path) and os.path.isdir(new_path):
            p_l = len(new_path)
            return [dir[p_l:] for dir in os.listdir(new_path) if os.path.isfile(dir)]

    def get_subfolders_in_folder(self, game_id: str, path: str) -> Optional[List[str]]:
        new_path = self.get_contained_paths(game_id, path)
        if new_path is None:
            return None
        if os.path.exists(new_path) and os.path.isdir(new_path):
            p_l = len(new_path)
            return [dir[p_l:] for dir in os.listdir(new_path) if os.path.isdir(dir)]

    def rename_object(self, game_id: str, path: str, final: str) -> Optional[bool]:
        new_path = self.get_contained_paths(game_id, path)
        final_path = self.get_contained_paths(game_id, final)
        if new_path is None or final_path is None:
            return None
        if os.path.exists(new_path) and not os.path.exists(final_path):
            os.rename(new_path, final_path)
            return True
        return False

    def remove_object(self, game_id: str, path: str) -> Optional[bool]:
        new_path = self.get_contained_paths(game_id, path)
        if new_path is None:
            return None
        if os.path.exists(new_path):
            try:
                os.remove(new_path)
            except:
                pass
            else:
                return True
        return False

    def make_folder(self, game_id: str, path: str) -> Optional[bool]:
        new_path = self.get_contained_paths(game_id, path)
        if new_path is None:
            return None
        if os.path.exists(new_path):
            try:
                os.mkdir(new_path)
            except:
                pass
            else:
                return True
        return False


def get_file_contents(path: str):
    with open(path, "r", encoding="utf8") as f:
        return f.read()


def write_to_file(path: str, contents: str):
    with open(path, "w", encoding="utf8") as f:
        f.write(contents)


class Framework:
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
        "interface",
        "description",
        "queue",
        "safe_file_access_class",
        "container_width",
        "container_height",
        "function_time_out",
        "max_actions_per_frame",
    )

    def __init__(
        self,
        interface: Union[Literal["console", "discord"], str],
        game_to_run: Optional[Union[str, Game]] = None,
        function_time_out: int = default_timeout,
        max_actions_per_frame: int = default_timeout,
    ) -> None:
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
        self.queue = []
        self.interface = interface
        self.container_height = None
        self.container_width = None
        self.function_time_out = function_time_out
        self.max_actions_per_frame = max_actions_per_frame
        self.safe_file_access_class = SafeFileAccess(default_games_folders)
        if not game_to_run is None:
            if isinstance(game_to_run, Game):
                error = load_game(game_to_run, interface)
                if isinstance(error, str):
                    raise Exception(error)
                self.game, self.description, self.first_frame, self.game_id = error
                self.select_game_and_error((self.game_id, self.game), interface)
            elif isinstance(game_to_run, str):
                self.select_game_and_error(game_to_run, interface)
            else:
                raise Exception("Invalid game type")

    def select_game_and_error(
        self, game_id: Union[str, Tuple[str, Game]], interface: str
    ):
        error = self.select_game(game_id, interface)
        if error:
            raise Exception(error)

    def set_container_size(self, size: Tuple[Optional[int], Optional[int]]):
        if not size[0] is None:
            self.container_width = size[0]
        if not size[1] is None:
            self.container_height = size[1]

    def run_game(
        self, user_input: str, info: Union[Dict, FrameworkAdditionalInfo]
    ) -> Optional[Union[Exception, str, StopFramework, ChangeInputs]]:
        if not self.ready:
            return Exception("Framework is not ready -> No game has been loaded")
        end, start = 0.0, 0.0
        self.frame_count += 1
        if self.frame_count == 0:
            self.time_between_frame_start = time.time()
        self.time_between_frame = self.time_between_frame_start - time.time()

        if not isinstance(info, dict):
            raise ValueError("Framework info ")
        else:
            debug_mode_enabled = info.get("debug_mode", False)
            user_id = info.get("user_id", "")
            username = info.get("username", "")

        if not self.send_new_frame:
            return self.old_frame

        # self.send_new_frame = False
        if self.frame_count == 0:
            return (
                self.first_frame
                + "\nValid inputs: %s\n" % self.accepted_inputs
                + (
                    get_localization("framework.debug.frame_time", (end - start)) + "\n"
                    if debug_mode_enabled
                    else ""
                )
            )

        if not user_input:
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

        file_input: Optional[
        List[
            Dict[Literal["type", "key", "value"], Optional[Union[List[str], str, bool]]]
        ]
    ] = (
            []
        )
        for idx in range(len(self.queue)):
            i = self.queue.pop(0)
            if i:
                pass
            elif isinstance(i, dict):
                key, item = get_only_item_in_dict(i)
                ################################################################################################
                if key == "does_object_exist":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.does_file_exist(
                                self.game_id, item
                            ),
                        }
                    )
                elif key == "get_file_contents":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.get_file_contents(
                                self.game_id, item
                            ),
                        }
                    )
                elif key == "write_to_file":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.write_to_file(
                                self.game_id, *get_only_item_in_dict(i)
                            ),
                        }
                    )
                elif key == "get_files_in_folder":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.get_files_in_folder(
                                self.game_id, item
                            ),
                        }
                    )
                elif key == "get_subfolders_in_folder":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.get_subfolders_in_folder(
                                self.game_id, item
                            ),
                        }
                    )
                elif key == "rename_object":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.rename_object(
                                self.game_id, *get_only_item_in_dict(i)
                            ),
                        }
                    )
                elif key == "make_folder":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.make_folder(
                                self.game_id, item
                            ),
                        }
                    )
                elif key == "remove_object":
                    file_input.append(
                        {
                            "type": key,
                            "key": item,
                            "value": self.safe_file_access_class.remove_object(
                                self.game_id, item
                            ),
                        }
                    )

                else:
                    raise ValueError("Unknown key: %s (%s)" % (key, item))

        start = time.time()

        try:
            output: Union[MainReturn, TimeoutError, Any] = (
                tge.function_utils.run_function_with_timeout(
                    self.game.main,
                    default_timeout,
                    input_id,
                    ExtraInfo(
                        old_frame=self.old_frame,
                        frame=self.frame_count,
                        deltatime=self.deltatime,
                        time_between_frame_start=self.time_between_frame,
                        user_id=user_id,
                        username=username,
                        file_request_data=file_input,
                        container_width=self.container_width,
                        container_height=self.container_height,
                    ),
                )
            )
            # output = game.main(input_id, user)
        except SystemExit:
            return Exception("SystemExit")
        except KeyboardInterrupt:
            return Exception(get_localization("exit.keyboard_interrupt"))
        except BaseException as e:
            return "\n" + get_localization(
                "framework.game.exception.unhandled", e, traceback.format_exc()
            )
        finally:
            now = time.time()
            self.deltatime = now - start
            self.time_between_frame_start = now
        ###############################################
        if isinstance(output, tge.function_utils.TimeoutResult):
            return Exception(
                get_localization("framework.game.error.timeout", default_timeout)
            )

        if output is None:
            return Exception("\n" + get_localization("framework.game.error.unhandled"))

        if not isinstance(output, dict):
            return Exception(
                "\n"
                + get_localization(
                    "framework.game.error.invalid_return_type", type(output)
                )
            )
    
        pre_actions: Optional[Union[Action, List[Action]]] = output.get("action", None)

        new_frame = output.get("frame")

        if new_frame is None:
            new_frame = ""
        elif not isinstance(new_frame, str):
            return Exception(
                "\n"
                + get_localization(
                    "framework.game.error.invalid_return_type.new_frame",
                    type(new_frame),
                )
            )

        if new_frame != "":
            if self.frame != new_frame:
                self.old_frame = self.frame
                self.frame = new_frame
                self.send_new_frame = True
        

        actions = self.prepare_actions(pre_actions)
        if isinstance(actions, BaseException):
            return actions

        r = self.handle_actions(actions, new_frame)  # type: ignore
        if not r is None:
            return r

        return self.frame

    def prepare_actions(self, pre_actions):
        if pre_actions is None:
            actions = []
        if pre_actions is None:
            return []

        if isinstance(pre_actions, dict):
            actions = [pre_actions]
        elif isinstance(pre_actions, list):
            actions = pre_actions
        else:
            return Exception(
                "\n"
                + get_localization(
                    "framework.game.error.invalid_return_type.action", type(pre_actions)
                )
            )

        if len(actions) > default_max_actions:
            return Exception(
                "\n"
                + get_localization(
                    "framework.game.error.too_many_actions_requested",
                    self.game_id,
                    actions,
                    default_max_actions,
                )
            )
        return actions

    def handle_actions(self, actions: List[Action], new_frame: Optional[str]):
        for a in actions:

            requested_value = a.get("value", "")
            action = a.get("action", "")

            if action != "":
                if action == "end":
                    if self.old_frame != new_frame:
                        self.ready = False
                        return StopFramework(self.frame)
                    return None
                elif action == "change_inputs":
                    if requested_value is None:
                        return Exception(
                            "\nReceived invalid input request when application tried changing inputs"
                        )
                    if isinstance(requested_value, (str, list)):
                        self.accepted_inputs, errors = load_inputs(requested_value)

                        if errors:
                            return Exception(
                                "\nReceived invalid input request when application tried changing inputs: %s"
                                % errors
                            )
                        return ChangeInputs(self.accepted_inputs, self.frame)
                    else:
                        return Exception(
                            "Invalid return value for changing keys: %s (%s)"
                            % (str(requested_value), type(requested_value))
                        )
                elif action == "unset":
                    pass
                elif action in [
                    "get_file_contents",
                    "set_file_contents",
                    "get_files_in_folder",
                    "rename_object",
                    "remove_object",
                    "make_folder",
                    "get_subfolders_in_folder",
                    "does_object_exist",
                ]:
                    self.queue.append({action: requested_value})
                else:
                    return Exception(
                        "\n"
                        + get_localization(
                            "framework.game.error.invalid_action", action
                        )
                    )
        return None

    def get_last_frame(self) -> str:
        return self.frame

    def select_game(
        self, game_id: Union[str, Tuple[str, Game]], interface: str
    ) -> Optional[str]:
        if isinstance(game_id, str):
            global GAMES
            try:
                game: Game = deepcopy(GAMES["games"][game_id]["game"])
            except TypeError as e:
                return get_localization(
                    "framework.game_selection.load.error.type_error", e
                )
        else:
            game_id, game = game_id

        try:
            result = tge.function_utils.run_function_with_timeout(
                game.setup, default_timeout, info={"user": "", "interface": interface}
            )
        except BaseException as e:
            return get_localization(
                "framework.game_selection.load.error",
                e,
                traceback.format_exc(),
            )
        if isinstance(result, tge.function_utils.TimeoutResult):
            return get_localization(
                "framework.game_selection.load.error.timeout", default_timeout
            )
        if not isinstance(result, (list, tuple)):
            return get_localization(
                "framework.game_selection.load.error.invalid_returns_from_setup", result
            )
        game_return_amount = len(result)
        if game_return_amount == 4:
            frame, requested_inputs, settings, pre_actions = result
        elif game_return_amount == 3:
            frame, requested_inputs, settings = result
            pre_actions = []
        elif game_return_amount == 2:
            frame, requested_inputs = result
            settings = {}
            pre_actions = []
        else:
            return get_localization(
                "framework.game_selection.load.error.invalid_returns_from_setup",
                game_return_amount,
            )
        if settings is None:
            settings = {}
        if not isinstance(frame, str):
            return "Invalid frame type, expected string but got %s" % type(frame)
        if not isinstance(settings, dict):
            return "Invalid settings type, expected dict but got %s" % type(settings)

        actions = self.prepare_actions(pre_actions)
        
        if isinstance(actions, BaseException):
            print(actions)
            return "Error"

        r = self.handle_actions(actions, None) # type: ignore
        if isinstance(r, ChangeInputs):
            return "Game requested to change inputs before game started"
        elif isinstance(r, StopFramework):
            return "Game requested to end before even starting"
        elif isinstance(r, Exception):
            return "Exception during action execution during game setup"

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
        self.queue = []
        self.game_id = game_id
        return None

    def select_game_from_user(
        self, user: str, key: Union[str, int]
    ) -> Union[Exception, str, SelectedGame, StopFramework]:
        send_string = (
            get_localization("framework.game_selection.selected_name", user) + "\n"
        )
        game_amount = len(GAMES["games"])

        # No need for the user to manually select a game if there is just a single game
        if game_amount == 1:
            game_id: str = [*GAMES["games"]][0]
            self.select_game_and_error(game_id, self.interface)
            return SelectedGame(GAMES["games"][game_id]["name"], game_id)

        if game_amount == 0:
            return StopFramework(
                get_localization("framework.game_selection.no_games_available")
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
                    get_localization("framework.game_selection.no_such_game", key)
                )
            if isinstance(games_based_on_selection, str):
                games_based_on_selection = [games_based_on_selection]
            game_id = games_based_on_selection[key]
            self.select_game_and_error(game_id, self.interface)
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
            get_localization("framework.game_selection.written", self.written) + "\n"
        )

        # Store games and insert them into a game list
        game_list_string = ""
        all_games = GAMES["games"]

        games_based_on_selection = tge.tbe.strict_autocomplete(self.written, all_games)

        if len(games_based_on_selection) == 0:
            send_string += get_localization(
                "framework.game_selection.no_games_found", self.written
            )
            return send_string
        if isinstance(games_based_on_selection, str):
            games_based_on_selection = [games_based_on_selection]

        if SELECT_FIRST:
            game_id = games_based_on_selection[0]
            self.select_game_and_error(game_id, self.interface)
            return SelectedGame(GAMES["games"][game_id]["name"], game_id)

        for game in games_based_on_selection:

            game_list_string += "\n" + get_localization(
                "framework.game_selection.individual_game",
                GAMES["games"][game]["name"],
                game,
            )
        send_string += get_localization(
            "framework.game_selection.game_list", game_list_string
        )

        return send_string


# def start_framework():
#     global id
#     id, user = wait_for_async_function(start)

#     while True:
#         game_id = select_game_from_user(user)

#         stuff = select_game(game_id)
#         if isinstance(stuff, str):
#             wait_for_async_function(
#                 send, id, get_localization("framework.game.start.error", stuff)
#             )
#             request_input()
#             continue
#         first_frame, inputs, game, give_old_frame = stuff
#         run_game(game, game_id, first_frame, inputs, give_old_frame)


def has_callable(module: Callable, name: str, dir: str):
    if module is None:
        return get_localization("framework.import.error.missing_game_class", dir, name)
    if not hasattr(module, name):
        return get_localization("framework.import.error.missing_game_class", dir, name)

    if not callable(getattr(module, name)):
        return get_localization("framework.import.error.invalid_game_class", dir, name)


def find_imported_files(module_path, base_dir):
    """Recursively finds all files imported in a module's __init__.py"""
    files = set()

    if not os.path.exists(module_path):
        return files

    with open(module_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=module_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                files.update(resolve_module(alias.name, base_dir))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                files.update(resolve_module(node.module, base_dir))
    return files


def resolve_module(module_name, base_dir):
    """Resolves a module name to a file path"""
    module_path = None
    try:
        spec = import_util.find_spec(module_name)
        if spec and spec.origin:
            module_path = spec.origin
    except ModuleNotFoundError:
        return set()

    if module_path and module_path.startswith(base_dir):
        return {module_path}
    return set()


def find_all_files(lib_path: str) -> List[str]:
    """Recursively finds all imported files in a library's __init__.py"""
    init_file = os.path.join(lib_path, "__init__.py")
    all_files = set()

    if os.path.exists(init_file):
        all_files.add(init_file)
        imported_files = find_imported_files(init_file, lib_path)

        for file in imported_files:
            if file not in all_files:
                all_files.add(file)
                if file.endswith("__init__.py"):  # If it's another package, scan deeper
                    all_files.update(find_imported_files(file, lib_path))

    return list(all_files)


def remove_comment_from_line(line: str):
    return line.split("#")[0].rstrip()


def is_module_allowed(modules: list[str], game_id: str, line_id: int):
    def is_module_in_allowed_modules(module: list[str], allowed: RecursiceModuleType):
        for item in allowed:
            if isinstance(item, str):
                if item == module[0]:
                    return True
            elif isinstance(item, dict):

                key, key_item = get_only_item_in_dict(item)
                if key != module[0]:
                    continue
                if len(module) > 1:
                    return is_module_in_allowed_modules(module[1:], key_item)
                return False
            else:
                raise NotImplementedError(item, module)
        return False

    for m in modules:
        if is_module_in_allowed_modules(m.split("."), LOADED["allowed_modules"]):
            continue
        else:
            return get_localization(
                "framework.import.error.untrusted_import", game_id, line_id, m
            )
    return ""


def check_line_for_allowed_imports(game_id: str, line: str, line_id: int) -> str:
    check_if_normal = re.compile(r"^\s*import\s+\w+")
    check_if_sub_import = re.compile(r"^\s*from\s+\w+\s+import\s+[\w\s,()]+")
    extract_root = re.compile(r"^\s*(?:import|from)\s+(\w+)")
    extract_sub_module = re.compile(r"^\s*from\s+\w+\s+import\s+([\w\s,()]+)")
    modules: list[str]
    if check_if_normal.match(line):
        module = extract_root.match(line)
        assert module is not None
        module = module.group(1)
        modules = [module]
    elif check_if_sub_import.match(line):
        module = extract_root.match(line)
        sub_module = extract_sub_module.match(line)
        assert module is not None
        assert sub_module is not None
        modules = [
            module.group(1) + "." + sub.strip(" ()\n").split(" ")[0]
            for sub in sub_module.group(1).split(",")
        ]

    else:
        return ""
    return is_module_allowed(modules, game_id, line_id)


def split_python_file_by_lines(file_content: str) -> list[str]:
    """
    Split a Python file content into logical lines, handling both newlines and semicolons.
    Properly handles semicolons inside comments and strings.

    Args:
        file_content (str): The content of the Python file as a string

    Returns:
        list[str]: A list of strings, where each string is a logical line from the file
    """
    # First split by newlines
    newline_split = file_content.splitlines()

    result = []
    for line in newline_split:
        current_pos = 0
        line_length = len(line)
        current_segment = ""
        in_single_quote = False
        in_double_quote = False
        in_comment = False

        while current_pos < line_length:
            char = line[current_pos]

            # Handle comments
            if char == "#" and not (in_single_quote or in_double_quote):
                in_comment = True
                current_segment += char
                current_pos += 1
                continue

            # Handle string literals
            if char == "'" and not in_double_quote and not in_comment:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote and not in_comment:
                in_double_quote = not in_double_quote

            # Handle escaped quotes
            if char == "\\" and (in_single_quote or in_double_quote):
                current_segment += char
                current_pos += 1
                if current_pos < line_length:  # Add the escaped character
                    current_segment += line[current_pos]
                    current_pos += 1
                continue

            # Handle semicolons
            if char == ";" and not (in_single_quote or in_double_quote or in_comment):
                if current_segment.strip():
                    result.append(current_segment.strip())
                current_segment = ""
            else:
                current_segment += char

            current_pos += 1

        result.append(current_segment.strip())

    return result


def is_file_unsafe(file_path: str, game_id: str) -> str:
    """Checks if a file is safe to import"""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    lines = split_python_file_by_lines(source)
    idx = -len(unsafe_keywords)
    for line in lines:
        idx += 1
        if not line:
            continue
        error = check_line_for_allowed_imports(game_id, line, idx)
        if error:
            return error
    return ""


def get_callable(dir: str) -> Tuple[str, Any]:
    try:
        spec = import_util.spec_from_file_location(
            dir, default_cache_folder + "/__init__.py"
        )
        assert spec is not None
        game = import_util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(game)
    except TypeError:
        return get_localization("framework.import.error.type_error", dir), None
    except BaseException as e:
        return get_localization("framework.import.error.error", dir, e), None
    return "", game


def copy_game_to_cache(folder: str):
    shutil.rmtree(default_cache_folder)
    os.mkdir(default_cache_folder)

    bad_keywords_cache = ""
    for nono in unsafe_keywords:
        bad_keywords_cache += "%s=None\n" % nono

    for root, dirs, files in os.walk(folder, topdown=False):
        for dir in dirs:
            os.mkdir(os.path.join(default_cache_folder, dir))
        for file in files:
            full_path = os.path.join(root, file)
            ext = os.path.splitext(full_path)[-1]
            if ext == ".py":
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                content = bad_keywords_cache + content
                with open(
                    os.path.join(default_cache_folder, file), "w", encoding="utf-8"
                ) as f:
                    f.write(content)
            elif ext in [".pyc"]:
                continue
            else:
                shutil.copyfile(full_path, os.path.join(default_cache_folder, file))


def initialize_games():
    all_error = []

    for game_folder in default_games_folders:
        sys.path.append(game_folder)
        for root, dirs, files in os.walk(game_folder, topdown=False):
            if root == game_folder:
                for dir in dirs:
                    # copy dir into other cache folder
                    full_dir = os.path.join(root, dir)
                    copy_game_to_cache(full_dir)
                    # print(full_dir)

                    files = find_all_files(default_cache_folder)
                    get_out = True
                    for file in files:
                        file_name = file[len(default_cache_folder) :]
                        reason = is_file_unsafe(file, full_dir + file_name)
                        if reason:
                            all_error.append(reason)
                            break
                    else:
                        get_out = False
                    if get_out:
                        continue
                    error, game = get_callable(dir)
                    if error:
                        all_error.append(error)
                        continue

                    error = has_callable(game, "Game", dir)
                    if error:
                        all_error.append(error)
                        continue

                    if os.path.exists(
                        os.path.join(default_cache_folder, "requirements.txt")
                    ):
                        with open(
                            os.path.join(default_cache_folder, "requirements.txt")
                        ) as f:
                            required_modules = f.read().split("\n")

                        required_libs = []
                        for mod in required_modules:
                            if tge.library_utils.is_library_installed(mod):
                                continue
                            required_libs.append(mod)
                        if len(required_libs) != 0:
                            log(
                                get_localization(
                                    "framework.import.requirements.missing",
                                    dir,
                                    ",\n".join(
                                        [
                                            get_localization(
                                                "framework.import.requirements.missing.single",
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
                                        "framework.import.requirements.installing"
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
                                            "framework.import.requirements.error",
                                            send_string,
                                        ),
                                        ERROR,
                                    )
                                else:
                                    log(
                                        get_localization(
                                            "framework.import.requirements.success"
                                        ),
                                        INFO,
                                    )
                                restart_program()

                    error = add_game_to_game_list(game.Game, "")

                    if error:
                        traceback.print_exc()
                        all_error.append(
                            get_localization("framework.import.error.load", dir, error)
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

reload_plugins(default_plugin_folder)

initialize_games()

clear_cache()

__all__ = [
    "Framework",
    "is_valid_game_id",
    "reload_plugins",
    "load_plugin",
    "SelectedGame",
    "StopFramework",
    "ChangeInputs",
    "SelectedGame",
]
