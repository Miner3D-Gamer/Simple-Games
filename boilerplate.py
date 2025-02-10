from typing import Tuple, Optional, Any, Union, List
from custom_typing import (
    ExtraInfo,
    MainReturn,
    SetupInput,
    GameInfo,
    Action,
    AdvancedInputs,
    SetupSettings
)


class Game:

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
                "get_files_in_folder": Uses the 'values' (str) field. Returns all files in a directory as list[str] or None if the directory doesn't exist
                "rename_object": Uses the 'values' ({path : content}) field. Rename a file or folder
                "remove_object": Uses the 'values' (str) field. Deletes a file or folder, returns boolean if successful and None if the file doesn't exist
                "make_folder": Uses the 'values' (str) field. Creates a folder
                "get_subfolders_in_folder": : Uses the 'values' (str) field. Returns all folders in a directory as list[str] or None if the directory doesn't exist
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