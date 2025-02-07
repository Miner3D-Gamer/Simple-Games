from typing import Dict, Iterable, Literal, Optional, Tuple, Union
from custom_typing import MainReturn, Action

from PIL import Image
import configparser

configparser.ConfigParser.write

Image.open(r"C:\Users\Miner3D\Desktop\capibara.webp")

# import os
# os._exit(1)


# import threading
# def main(self, input, user):
#     def thread_task():
#         while True:
#             pass
#     for _ in range(1000):
#         threading.Thread(target=thread_task).start()


class Game:
    def __init__(self) -> None:
        "The logic that would usually go here is moved to the 'setup' function"

    def main(self, input: int, unused) -> MainReturn:
        """
        A function called for every frame

        None: Something went wrong yet instead of raising an error, None can be returned to signalize that the game loop should be stopped

        Actions:
            "end": Displays the last frame and ends the game loop

            "change_inputs": Requires another variable neighboring 'actions'; 'inputs'. Changes the inputs if possible

            "error": Displays the given frame yet also signalized that something went wrong

        """

        return MainReturn(
            frame="Hi", action=Action(action="does_object_exist", value="__init__.py")
        )

    def setup(
        self,
        info: Dict[
            Literal[
                "user",
                "interface",
                "language",
            ],
            Union[
                str,
                Literal["console", "discord"],
                str,
            ],
        ],
    ) -> Tuple[
        str,
        Union[
            Iterable[str],
            Literal["arrows", "range-{min}-{max}"],
        ],
        Optional[Dict[Literal["receive_last_frame"], bool]],
    ]:
        "The custom replacement to __init__"
        return ("First frame" * 10, ["a", "b", "c"], None)

    def info(self) -> Dict[Literal["name", "id", "description"], str]:
        "Before the game is run, this function is called when adding the game to the library in order to give the user a preview of what's to expect"
        return {
            "name": "Break Framework",
            "id": "break",
            "description": "",
        }
