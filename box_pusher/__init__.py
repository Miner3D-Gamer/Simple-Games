from math import log
from typing import Literal
import json, os
from copy import deepcopy as copy


class Game:
    def __init__(self, width: int = 15, height: int = 10, boarder: str = "#") -> None:
        self.level = -1
        self.start_round()
        self.boarder = boarder
        

    def get_level(self, level: int) -> tuple[int, int, dict]:
        
        with open(os.path.dirname(__file__)+"/levels.json") as f:
            data = json.load(f)
        if level >= len(data):
            return {}
        return data[level]
    

    def load_level(self, data: dict) -> str:
        width = data["width"]
        height = data["height"]
        board = data["board"]

        self.generate_board(width, height)

        # Iterate over board to identify elements
        for y in range(height):
            for x in range(width):
                cell = board[y][x]
                if cell == "P":
                    self.spawn_player(x, y)
                elif cell == "R":
                    if not self.spawn_reset_button(x, y):
                        return f"Conflict while loading a reset button at position {x}, {y}"
                elif cell == "T":
                    if not self.spawn_trigger_pad(x, y):
                        return f"Conflict while loading a trigger pad at position {x}, {y}"
                elif cell == "#":
                    if not self.spawn_wall(x, y):
                        return f"Conflict while loading a wall at position {x}, {y}"

        return ""
    
    def spawn_reset_button(self, x, y):
        if self.get_item_at(x, y) == " ":
            self.board[y][x] = "R"
            return True
        return False

    def start_round(self) -> bool:
        self.player_exists = False
        self.level += 1
        data = self.get_level(self.level)
        if data == {}:
            return False
        errors = self.load_level(data)
        if errors:
            print(errors)
            return None
        return True

    def generate_board(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        board = []
        for y in range(height):
            board.append([" "] * width)
        self.board: list[list[str]] = board

    def spawn_wall(self, x: int, y: int) -> bool:
        if self.get_item_at(x, y) == " ":
            self.board[y][x] = "#"
            return True
        return False

    def spawn_trigger_pad(self, x: int, y: int) -> bool:
        if self.get_item_at(x, y) == " ":
            self.board[y][x] = "T"
            return True
        return False

    def spawn_box(self, x: int, y: int) -> bool:
        if self.get_item_at(x, y) == " ":
            self.board[y][x] = "B"
            return True
        return False

    def spawn_player(self, x: int, y: int) -> bool:
        
        if not self.get_item_at(x, y) == "#":
            self.player_exists = True
            self.pos_x = x
            self.pos_y = y
            self.board[y][x] = "P"
            return True
        return False

    def get_board(self):
        str = "#" * (self.width + 2)
        str += "\n"
        for i in self.board:
            i = ["#", *i, "#"]
            str += "".join(i)
            str += "\n"
        str += "#" * (self.width + 2)

        return "".join([self.decode_visualization(letter) for letter in str])

    def is_board_been_completed(self) -> bool:  # engrish
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == "T":
                    return False
        return True

    def decode_visualization(self, item: str) -> str:
        table = {"#": self.boarder}

        return table.get(item, item)

    def get_item_at(self, x: int, y: int) -> str:
        if x >= self.width or x == -1:
            return "#"
        if y >= self.height or y == -1:
            return "#"
        return self.board[y][x]

    def move(self, direction: int) -> None:
        if direction == 0:  # Left
            self.move_by(self.pos_x, self.pos_y, -1, 0)
        elif direction == 1:  # Up
            self.move_by(self.pos_x, self.pos_y, 0, -1)
        elif direction == 2:  # Down
            self.move_by(self.pos_x, self.pos_y, 0, 1)
        elif direction == 3:  # Right
            self.move_by(self.pos_x, self.pos_y, 1, 0)

    def minimize(self, num: int) -> Literal[1] | Literal[-1]:
        return num // abs(num)

    def move_by(self, current_x, current_y, offset_x, offset_y):

        current_item: str = self.board[current_y][current_x]
        target_x = current_x + offset_x
        target_y = current_y + offset_y
        item = self.get_item_at(target_x, target_y)
        if item in ["#", "b"]:
            return False
        if item == "B":
            successful = self.move_by(
                target_x,
                target_y,
                self.minimize(offset_x) if offset_x != 0 else 0,
                self.minimize(offset_y) if offset_y != 0 else 0,
            )
            if not successful:
                return False

        if item == "R":
            self.level -= 1
            self.start_round()
            return
        
        if item == "T":
            self.board[target_y][target_x] = current_item.lower()
        else:
            self.board[target_y][target_x] = current_item.upper()
        

        self.board[current_y][current_x] = " " if current_item.isupper() else "T"

        if current_item.upper() == "P":
            self.pos_x, self.pos_y = target_x, target_y
        return True

    def main(self, input: int, user: str) -> None | str | list:
        if not (input > -1 and input < 4):
            return None
        if not self.player_exists:
            return None
        self.move(input)
        done = self.is_board_been_completed()
        if done:
            not_done = self.start_round()
            if not not_done:
                if not_done is None:
                    return None
                return [self.get_board() + "\nBoard is Completed"]
        return self.get_board()

    def setup(self, user) -> str:
        return self.get_board()

    def info(self) -> list[str, str, list[str] | str]:
        return ["box_pusher", "Box Pusher", "arrows"]


if __name__ == "__main__":
    ...

