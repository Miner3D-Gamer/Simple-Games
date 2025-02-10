from typing import (
    Any,
    Literal,
    Dict,
    Union,
    Iterable,
    Tuple,
    Optional,
    TypeAlias,
    TypedDict,
    List,
    get_origin,
    get_args,
)

# class Requirements:
#     modules:List[str]
#     python_version: str


class FrameworkAdditionalInfo(TypedDict):
    user_id: str
    username: str
    debug_mode: bool


class Preset(TypedDict):
    name: str
    value: str
    type: Literal["literal", "genex"]
    conditions: Optional[List[Dict[str, Union[str, List[str]]]]]
    split: str
    inserts: Optional[str]


class SetupSettings(TypedDict):
    ...

class ExtraInfo(TypedDict):
    username: str
    user_id: str
    old_frame: str
    frame: int
    deltatime: float
    time_between_frame_start: float
    file_request_data: Optional[
        List[
            Dict[Literal["type", "key", "value"], Optional[Union[List[str], str, bool]]]
        ]
    ]
    container_width: Optional[int]
    container_height: Optional[int]


class AdvancedInputs(TypedDict):
    type: Literal["preset", "custom"]
    value: Union[str, List[str]]


# INPUTS: TypeAlias = List[str]
# INPUTS: TypeAlias = Union[
#     Union[str, List[str], Tuple[str, ...]],
#     Union[Literal["arrows", "range-{min}-{max}", "{min}-{max}"], str],
#     List[AdvancedInputs],
# ]


class Action(TypedDict):
    action: Literal[
        "end",
        "change_inputs",
        "unset",
        "get_file_contents",
        "write_to_file",
        "get_files_in_folder",
        "rename_object",
        "remove_object",
        "make_folder",
        "get_subfolders_in_folder",
        "does_object_exist",
    ]
    value: Optional[Union[List[str], str, Dict[str, str]]]


class MainReturn(TypedDict):
    frame: str
    action: Optional[Union[Action, List[Action]]]



class SetupInput(TypedDict):
    user: str
    interface: Union[Literal["console", "discord"], str]
    language: str


class GameInfo(TypedDict):
    name: str
    id: str
    description: str


class Game:

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self

    def __init__(self) -> None:
        "The logic that would usually go here is moved to the 'setup' function. Type annotation may be used here."

    def main(
        self,
        input: int,
        info: Optional[ExtraInfo],
    ) -> Optional[MainReturn]:
        """
        A function called for every frame

        To signal an error, raise an Exeption anytime, or use quit()/return None to signalize something went wrong without any debug info

        Actions:
            Misc:
                "end": Displays the last frame and ends the game loop
                "change_inputs": Uses the 'values' field. Changes the inputs if possible
                "unset": Does nothing, can be used when returning None for the action would be inconvinient

            I/O:
                "get_file_contents": Uses the 'values' (str) field. Get the file contents as string or None if the file doesn't exist
                "write_to_file": Uses the 'values' ({path : content}) field. Creates and writes to a file
                "get_files_in_folder": Uses the 'values' (str) field. Returns all files in a directory as List[str] or None if the directory doesn't exist
                "rename_object": Uses the 'values' ({path : content}) field. Rename a file or folder
                "remove_object": Uses the 'values' (str) field. Deletes a file or folder, returns boolean if successful and None if the file doesn't exist
                "make_folder": Uses the 'values' (str) field. Creates a folder
                "get_subfolders_in_folder": : Uses the 'values' (str) field. Returns all folders in a directory as List[str] or None if the directory doesn't exist
                "does_object_exist": Uses the 'values' (str) field. Returns a boolean if a folder or file exist
        """

    def setup(
        self,
        info: SetupInput,
    ) -> Tuple[str, List[str], Optional[SetupSettings], Optional[Union[Action, List[Action]]]]:
        """
        The custom replacement to __init__.
        I/O actions can be used here to set up settings or get files before the user interacts with the game.
        """
        return ("First frame", ["a", "b", "c"], None, None)

    def info(self) -> GameInfo:
        "Before the game is run, this function is called when adding the game to the library in order to give the user a preview of what to expect"
        return {
            "name": "Custom game",
            "id": "example_game",
            "description": "A simple game",
        }


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
