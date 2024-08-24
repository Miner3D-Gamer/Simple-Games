# from math import log
from typing import Literal
import json, os
from copy import deepcopy as copy
from tge.manipulation.list_utils import decompress_list_of_lists

# Reset/Start: self.start_round()


class Game:
    def __init__(self) -> None:
        self.level_id = -1
        self.first_round = True
        self.formatting = "left"
        self.menu_id = "main"
        print(self.menu())
        os.kill(os.getpid(), 9)

    def format_string(
        self, string: str, length: int, filler: str, min_buffer: int = 2
    ) -> str:
        if self.formatting == "center":
            return string.center(length, filler)
        elif self.formatting == "left":
            return string.rjust(min_buffer + len(string), filler).ljust(length, filler)
        elif self.formatting == "right":
            return string.ljust(min_buffer + len(string), filler).rjust(length, filler)
        return string

    def generate_menu(self, options: list[str], width: int):
        menu = []
        border = self.format_string("", width, "#")
        menu.append(border)
        for i, arrow in enumerate("⬆➡⬅⬇"):
            menu.append(self.format_string(" %s %s "%(arrow, options[i]), width, "#"))
        menu.append(border)
        return ("\n".join(menu)).replace("#", "█")

    def menu(self):
        if self.menu_id == "main":
            return self.generate_menu(["Play", "Not implemented", "Settings", "Exit"], 25)
        elif self.menu_id == "settings":
            return self.generate_menu(["Main Menu", "Not implemented", "Not implemented", "Not implemented"], 25)


    def get_all_world_names(self) -> list[dict]:
        worlds_folder = os.path.dirname(__file__) + "/worlds"
        json_files = [f for f in os.listdir(worlds_folder) if f.endswith(".json")]

        return json_files

    def get_level_order(self) -> list[str]:
        with open(os.path.dirname(__file__) + "/levels.json") as f:
            data = json.load(f)
        return data["level_order"]

    def get_level(self, level: int) -> tuple[int, int, dict]:

        with open(os.path.dirname(__file__) + "/levels.json") as f:
            data = json.load(f)

        return data["levels"].get(level, {})

    def load_level(self, data: dict) -> str:
        width = data["width"]
        height = data["height"]
        board = decompress_list_of_lists(data["board"], width)
        id_board = decompress_list_of_lists(data["id_board"], width)
        if not self.first_round:
            quick_copy_of_board = copy(self.board)
            quick_copy_of_id_board = copy(self.id_board)
            quick_copy_of_metadata = copy(self.metadata)

        self.metadata = data["metadata"]
        self.continue_condition = self.metadata["continue_condition"]

        self.generate_board(width, height)
        self.id_board = id_board

        print([i for i in range(height)])

        player_spawn_queue = {}

        # Iterate over board to identify elements
        for y in range(height):
            for x in range(width):

                cell: str = board[y][x]
                c = cell
                cell = cell.upper()
                if cell == "P":
                    player_spawn_queue.update({id_board[y][x]: (x, y)})

                elif cell == "R":
                    if not self.spawn_reset_button((x, y)):
                        return f"Conflict while loading a reset button at position {x}, {y}"
                elif cell == "T":
                    if not self.spawn_trigger_pad((x, y)):
                        return (
                            f"Conflict while loading a trigger pad at position {x}, {y}"
                        )
                elif cell == "S":
                    if not self.spawn_secret((x, y)):
                        return (
                            f"Conflict while loading a secret tile at position {x}, {y}"
                        )
                elif cell == "B":
                    if not self.spawn_box((x, y)):
                        return (
                            f"Conflict while loading a trigger pad at position {x}, {y}"
                        )
                elif cell == "#":
                    if not self.spawn_wall((x, y)):
                        return f"Conflict while loading a wall at position {x}, {y}"
                if c.islower():
                    self.lower_character((x, y))

        if self.first_round:
            id = "0"
        else:
            previous_player_position = self.find_first_occurrence_on_board(
                quick_copy_of_board, "P"
            )
            id = quick_copy_of_id_board[previous_player_position[1]][
                previous_player_position[0]
            ]
        position = player_spawn_queue.pop(id, None)

        if position is None:
            raise BaseException(
                f"On level {self.level_id} no valid player position has been evaluated. Last trigger id: {id} ({str(type(id))[8:-2]}), vs Player spawn queue: {player_spawn_queue}"
            )
        for i in player_spawn_queue:
            self.spawn_box(player_spawn_queue[i])
            self.lower_character(player_spawn_queue[i])

        self.spawn_player(position)

        self.first_round = False
        return ""

    def find_first_occurrence_on_board(
        self, board: list[list[str]], char: str, regardless_of_casing: bool = True
    ) -> tuple[int, int]:
        if regardless_of_casing:
            char = char.lower()
        for strip_id in range(len(board)):
            strip = board[strip_id]
            for character_id in range(len(strip)):
                character = strip[character_id]
                if character.lower() == char:
                    return (character_id, strip_id)
        return (-1, -1)

    def lower_character(self, coords: tuple[int, int]):
        x, y = coords
        if self.get_item_at((x, y)) != "#":
            self.board[y][x] = self.board[y][x].lower()
            return True
        return False

    def destroy_character(self, coords: tuple[int, int]):
        x, y = coords
        char = self.get_item_at((x, y))
        if self.is_in_bounce(coords):
            self.board[y][x] = "T" if char.islower() else " "
            return True
        return False

    def add_to_x(self, coords: tuple[int, int], value):
        return coords[0] + value, coords[1]

    def add_to_y(self, coords: tuple[int, int], value):
        return coords[0], coords[1] + value

    def add_coordinates(self, coords: tuple[int, int], coords2: tuple[int, int]):
        return coords[0] + coords2[0], coords[1] + coords2[1]

    def destroy_all_connected(self, coords: tuple[int, int]):
        char = self.get_item_at(coords)
        id = self.get_id_at(coords)
        self.destroy_character(coords)

        coords_to_check = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for coord in coords_to_check:
            new_coords = self.add_coordinates(coords, coord)
            new_char = self.get_item_at(new_coords)
            if new_char == char and self.get_id_at(new_coords) == id:
                self.destroy_all_connected(new_coords)

    def spawn_secret(self, coords: tuple[int, int]):
        x, y = coords
        if self.get_item_at((x, y)) == " ":
            self.board[y][x] = "S"
            return True
        return False

    def spawn_reset_button(self, coords: tuple[int, int]):
        x, y = coords
        if self.get_item_at((x, y)) == " ":
            self.board[y][x] = "R"
            return True
        return False

    def start_round(self) -> bool:
        self.player_exists = False
        self.level_id += 1
        levels = self.get_level_order()
        if self.level_id >= len(levels):
            return False
        data = self.get_level(levels[self.level_id])
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
        self.board: list[list[str],] = board

    def spawn_wall(self, coords: tuple[int, int]) -> bool:
        x, y = coords
        if self.get_item_at((x, y)) == " ":
            self.board[y][x] = "#"
            return True
        return False

    def spawn_trigger_pad(self, coords: tuple[int, int]) -> bool:
        x, y = coords
        if self.get_item_at((x, y)) == " ":
            self.board[y][x] = "T"
            return True
        return False

    def spawn_box(self, coords: tuple[int, int]) -> bool:
        x, y = coords
        if self.get_item_at((x, y)) == " ":
            self.board[y][x] = "B"
            return True
        return False

    def spawn_player(self, coords: tuple[int, int]) -> bool:
        x, y = coords
        if not self.get_item_at((x, y)) == "#":
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

        return self.decode_visualization(str)

    def is_board_been_completed(self) -> bool:  # engrish
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == "T":
                    return False
        return True

    def decode_visualization(self, item: str) -> str:
        table = {"#": "█", "H": "█"}

        return "".join([table.get(letter, letter) for letter in item])

    def is_in_bounce(self, coords: tuple[int, int]) -> bool:
        if coords[0] >= self.width or coords[0] == -1:
            return False
        if coords[1] >= self.height or coords[1] == -1:
            return False
        return True

    def get_item_at(self, coords: tuple[int, int]) -> str:
        if not self.is_in_bounce(coords):
            return "#"
        return self.board[coords[1]][coords[0]]

    def get_id_at(self, coords: tuple[int, int]) -> str:
        if not self.is_in_bounce(coords):
            return 0
        return self.id_board[coords[0]][coords[1]]

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
        item = self.get_item_at((target_x, target_y))
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
        if item == "S":
            self.destroy_all_connected((target_x, target_y))
            return
        if item == "R":
            self.level_id -= 1
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

    def main(self, input: int, user: str) -> None | dict:
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
                return {
                    "frame": self.get_board() + "\nBoard is Completed",
                    "action": "end",
                }
        return {"frame": self.get_board()}

    def setup(self, user) -> tuple[str, str]:
        return self.get_board(), "arrows"

    def info(self) -> dict:
        return {"id": "box_pusher", "name": "Box Pusher"}


if __name__ == "__main__":
    ...
