from typing import Tuple, Optional, Any, Union, List
from custom_typing import (
    ExtraInfo,
    MainReturn,
    SetupInput,
    INPUTS,
    GameInfo,
    Action,
    AdvancedInputs,
)


class Game:

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
            "description": "A complex game",
        }
