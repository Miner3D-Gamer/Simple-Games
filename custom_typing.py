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
#     modules:list[str]
#     python_version: str


class Preset(TypedDict):
    name: str
    value: str
    type: Literal["literal", "code"]
    inserts: Optional[List[Union[str, List[str]]]]
    valid: Union[str, List[str]]


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


class FrameworkAdditionalInfo(TypedDict):
    user_id: str
    username: str
    debug_mode: bool


class AdvancedInputs(TypedDict):
    presets: Union[str, list[str]]
    custom: list[str]


INPUTS: TypeAlias = Union[
    Union[str, list[str], Tuple[str, ...]],
    Union[Literal["arrows", "range-{min}-{max}", "{min}-{max}"], str],
    AdvancedInputs,
]


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
    value: Optional[Union[INPUTS, str, Dict[str, str]]]


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
        "The logic that would usually go here is moved to the 'setup' function"

    def main(
        self,
        input: int,
        info: Optional[ExtraInfo],
    ) -> Optional[MainReturn]:
        """
        A function called for every frame

        None: Something went wrong yet instead of raising an error, None can be returned to signalize that the game loop should be stopped

        Actions:
            "end": Displays the last frame and ends the game loop

            "change_inputs": Requires another variable neighboring 'actions'; 'inputs'. Changes the inputs if possible

            "error": Displays the given frame yet also signalized that something went wrong

        """

    def setup(
        self,
        info: SetupInput,
    ) -> Tuple[str, INPUTS, Optional[Union[Action, List[Action]]]]:
        "The custom replacement to __init__"
        return ("First frame", ["a", "b", "c"], None)

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
