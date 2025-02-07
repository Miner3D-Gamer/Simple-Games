from typing import Literal, Dict, Union, Iterable, Tuple, List, Optional


class Game:
    def __init__(self) -> None:
        "The logic that would usually go here is moved to the 'setup' function"

    def main(self, input: int, user: str) -> Union[
        None,
        Dict[
            Union[Literal["frame"], Optional[Literal["action", "inputs"]]],
            Union[
                str,
                Optional[Literal["end", "change_inputs"]],
                Optional[Union[Iterable, Literal["arrows", "range-{min}-{max}"]]],
            ],
        ],
    ]:
        """
        A function called for every frame

        None: An error occurred yet instead of raising an error, None is returned to signalize that the game loop should be stopped

        Actions:
            "end": Displays the last frame and ends the game loop

            "change_inputs": Requires another variable neighboring 'actions'; 'inputs'. Changes the inputs if possible

            "error": Displays the given frame yet also signalized that something went wrong

        """
        print(input)
        return {"frame": f"Frame {input}"}

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
            Iterable,
            Literal["arrows", "range-{min}-{max}"],
            Dict[Literal["receive_last_frame"], bool],
        ],
    ]:
        "The custom replacement to __init__"
        return ("First frame", [*"abcdefgh"])

    def info(self) -> Dict[Literal["name", "id", "description"], str]:
        "Before the game is run, this function is called when adding the game to the library in order to give the user a preview of what's to expect"
        return {
            "name": "Minesweeper",
            "id": "minesweeper",
            "description": "A simple puzzle game",
        }
    
    def generate_board(self, width:int, height:int, mine_count:int):
        string = ""
        
        for w in range(width):
            for h in range(height):
                print(w, h)
