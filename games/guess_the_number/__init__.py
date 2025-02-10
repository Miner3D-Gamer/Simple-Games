from typing import Tuple, Optional, Any, Union, List
from custom_typing import (
    ExtraInfo,
    MainReturn,
    SetupInput,
    GameInfo,
    Action,
    AdvancedInputs,
)
import random


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
        
        select = False
        if input < 10:
            self.selected = int(str(self.selected) + str(input))
        elif input == 10:
            tmp = str(self.selected)[:-1]
            self.selected = int(tmp if tmp else 0)
        elif input == 11:
            select = True
        else:
            self.selected = -self.selected

        frame_a, action = self.handle_num(self.selected, select)
        frame = f"Guess the number between {self.lowest} and {self.highest}\n>"
        frame += frame_a

        return MainReturn(frame=frame, action=action)

    def handle_num(self, num: int, selected: bool) -> Tuple[str, Action]:
        
        if selected:
            self.selected = 0
            if num == self.value:
                return "%s - You won"%num, Action(action="end", value=None)
            elif num > self.value:
                if num < self.highest:
                    self.highest = num
                return "%s - Too high"%num, Action(action="unset", value=None)
            elif num < self.value:
                if num > self.lowest:
                    self.lowest = num
                return "%s - Too low"%num, Action(action="unset", value=None)
        
        

        self.selected = num
        return "%s" % num, Action(action="unset", value=None)

    def setup(
        self,
        info: SetupInput,
    ) -> Tuple[str, list[str], Optional[Union[Action, List[Action]]]]:
        "The custom replacement to __init__"
        self.selected = 0
        self.min = 0
        self.max = 100
        self.last_guess = None
        self.lowest = self.min
        self.highest = self.max
        self.value = random.randint(self.min, self.max)
        return (
            "Guess a number between 0 and 100\n>",
            ["0-9", "BACKSPACE", " ", "-"],
            None,
        )

    def info(self) -> GameInfo:
        "Before the game is run, this function is called when adding the game to the library in order to give the user a preview of what to expect"
        return {
            "name": "Guess the Number",
            "id": "guess_the_number",
            "description": "A complex game about guessing an arbitrary number",
        }
