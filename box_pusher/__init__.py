# from math import log
from typing import Literal
import json, os
from copy import deepcopy as copy
from tge.manipulation.list_utils import decompress_list_of_lists
import ijson

# Reset/Start: self.start_round()


class Game:
    def __init__(self) -> None:
        self.level_id = -1
        self.first_round = True
        self.formatting = "left"
        self.menu_id = "main"
        self.current_action = "menu"
        self.worlds_folder = os.path.dirname(__file__) + "/worlds"
        self.current_world = ""
        self.current_world_selection_page = 0

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

    def get_metadata(self, file_path: str):
        with open(file_path, "r") as file:
            parser = ijson.parse(file)
            found = False
            metadata = {}
            current_key = None
            current_object = metadata

            for prefix, event, value in parser:
                if found:
                    if event == "map_key":
                        current_key = value
                    elif event in ("start_map", "start_array"):
                        new_object = {} if event == "start_map" else []
                        if isinstance(current_object, list):
                            current_object.append(new_object)
                        else:
                            current_object[current_key] = new_object
                        current_object = new_object  # Move deeper
                    elif event in ("end_map", "end_array"):
                        parent_key = prefix.rsplit(".", 1)[0] if "." in prefix else None
                        if parent_key:
                            parent_prefix = parent_key.rsplit(".", 1)[0]
                            current_object = (
                                metadata
                                if parent_prefix == "metadata"
                                else current_object[parent_key]
                            )
                    elif event in ("string", "number", "boolean", "null"):
                        if isinstance(current_object, list):
                            current_object.append(value)
                        else:
                            current_object[current_key] = value

                if prefix == "metadata" and event == "start_map":
                    found = True
                elif prefix == "metadata" and event == "end_map":
                    break

        return metadata

    def generate_menu(self, options: list[str], width: int):
        menu = []
        border = self.format_string("", width, "#")
        menu.append(border)
        for i, arrow in enumerate(options):  # "⬅⬆⬇➡"
            menu.append(self.format_string(" %s %s " % (i + 1, options[i]), width, "#"))
        menu.append(border)
        return ("\n".join(menu)).replace("#", "█")

    def get_menu(self):
        if self.menu_id == "main":
            return self.generate_menu(
                ["Play", "Settings", "Info", "Exit"], 25
            )
        elif self.menu_id == "settings":
            return self.generate_menu(
                ["Main Menu", "Not implemented", "Not implemented", "Not implemented"],
                25,
            )
        elif self.menu_id == "world_selection":
            return self.generate_menu(
                ["Main menu", "Next Page"]
                + self.get_world_names_for_page(self.current_world_selection_page, 6)
                + ["Previous Page"],
                25,
            )
        elif self.menu_id == "info":
            return self.generate_menu(
                ["Main Menu", "Not implemented", "Not implemented", "Not implemented"],
                25,
            )
        
        return "Invalid menu ID: %s"%self.menu_id

    def get_world_names_for_page(self, page: int, page_size: int = 10) -> list[str]:
        return self.get_all_world_names()[page * page_size : (page + 1) * page_size]

    def get_world_from_page_and_index(
        self, page: int, index: int, page_size: int = 10
    ) -> str:
        print(page)
        global_index = page * page_size + index

        all_world_names = self.get_all_world_names()

        if 0 <= global_index < len(all_world_names):
            return all_world_names[global_index]
        else:
            raise IndexError("Invalid page or index")

    def get_all_world_names(self) -> list[str]:
        files = self.get_all_world_files()
        names = []
        for file in files:
            metadata = self.get_metadata(os.path.join(self.worlds_folder, file))
            name = metadata.get("name", "")
            if not name or not isinstance(name, str):
                name = os.path.splitext(file)[0]
            names.append(name)
        return names

    def get_all_world_files(self) -> list[dict]:

        json_files = [f for f in os.listdir(self.worlds_folder) if f.endswith(".json")]

        return sorted(json_files)

    def get_first_level_name(self, world: str) -> list[str]:
        with open(os.path.join(self.worlds_folder, world)) as f:
            data = json.load(f)
        metadata = data["metadata"]
        levels = data["levels"]
        del data

        for level in metadata["level_order"]:
            if level in levels:
                return level
        else:
            return ""

    def get_level(self, world: str, level: str) -> tuple[int, int, dict]:

        with open(os.path.join(self.worlds_folder, world)) as f:
            data = json.load(f)

        return data["levels"].get(level, {})

    def get_last_player_id(self):
        copy_of_board = copy(self.board)

        if self.first_round:
            id = "0"
        else:
            previous_player_position = self.find_first_occurrence_on_board(
                copy_of_board, "P"
            )
            id = self.id_board[previous_player_position[1]][previous_player_position[0]]

        return id

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

    def start_round(self, world: str) -> bool:
        self.player_exists = False

        data = self.get_level(world, self.level_id)
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
            self.start_round(self.current_world)
            return

        if item == "T":
            self.board[target_y][target_x] = current_item.lower()
        else:
            self.board[target_y][target_x] = current_item.upper()

        self.board[current_y][current_x] = " " if current_item.isupper() else "T"

        if current_item.upper() == "P":
            self.pos_x, self.pos_y = target_x, target_y
        return True

    def get_next_level(self):
        player_id = self.get_last_player_id()
        with open(os.path.join(self.worlds_folder, self.current_world), "r") as file:
            metadata = json.load(file)["levels"][self.level_id]["metadata"]
        exits = metadata.get("exits", {})
        next_level_name = exits.get(str(player_id), "")
        if isinstance(next_level_name, str):
            return next_level_name, False
        if isinstance(next_level_name, list):
            raise NotImplementedError("Optional level selection not implemented")
        if isinstance(next_level_name, int):
            return metadata["level_order"][next_level_name], False
        if isinstance(next_level_name, dict):
            # world, level, the end
            world = next_level_name.get("world", self.current_world)
            level = next_level_name.get("level", self.level_id)
            the_end = next_level_name.get("end", False)
            self.current_world = world
            return level, the_end

    def world_name_to_file(self, name: str) -> str:
        world_names = self.get_all_world_names()
        return self.get_all_world_files()[world_names.index(name)]

    def handle_menu(self, input: int):
        def change_menu(menu_id: str):
            self.menu_id = menu_id
            return {"frame": self.get_menu()}

        play = lambda: change_menu("world_selection")
        settings = lambda: change_menu("settings")
        main_menu = lambda: change_menu("main")

        def not_implemented():
            return {"frame": ""}

        def exit():
            return {
                "frame": "##########\n#Goodbye!#\n##########".replace("#", "█"),
                "action": "end",
            }

        def start():
            self.current_action = "playing"
            self.level_id = self.get_first_level_name(self.current_world)
            self.start_round(self.current_world)
            return {
                "frame": self.get_board(),
                "action": "change_inputs",
                "inputs": "arrows",
            }

        def change_world_selection_page(value: int):
            self.current_world_selection_page += value

        world_selection_next_page = lambda: change_world_selection_page(1)
        world_selection_previous_page = lambda: change_world_selection_page(1)

        def selected_world():
            world = self.get_world_from_page_and_index(
                self.current_world_selection_page, input - 2, 6
            )
            self.current_world = self.world_name_to_file(world)
            return start()

        info = lambda: change_menu("info")
        
        happenings = {
            "main": [play, settings, info, exit],
            "settings": [main_menu, not_implemented, not_implemented, not_implemented],
            "world_selection": [
                main_menu,
                world_selection_next_page,
                *[selected_world] * len(self.get_all_world_files()),
                world_selection_previous_page,
            ],
        }
        pass_func = lambda: {
            "frame": "Invalid menu ID: %s" % self.menu_id,
            "action": "end",
        }
        try:
            func = happenings.get(self.menu_id, [pass_func] * 4)[input]
        except IndexError:
            return pass_func()

        return func()

    def main(self, input: int, user: str) -> None | dict:

        if self.current_action == "playing":
            if not (input > -1 and input < 4):
                return None
            if not self.player_exists:
                return None
            self.move(input)
            done = self.is_board_been_completed()
            if done:
                ############################################################ NEXT LEVEL
                last_level_id = self.level_id
                self.level_id, the_end = self.get_next_level()
                if the_end:
                    return {
                        "frame": self.get_board() + "\nBoard is Completed",
                        "action": "end",
                    }
                if not self.level_id:
                    raise BaseException(
                        "Invalid level id to load: %s loaded with id %s in level %s"
                        % (self.level_id, self.get_last_player_id(), last_level_id)
                    )
                not_done = self.start_round(self.current_world)
                if not not_done:
                    if not_done is None:
                        return None
                    return {
                        "frame": self.get_board() + "\nBoard is Completed",
                        "action": "end",
                    }
            return {"frame": self.get_board()}
        elif self.current_action == "menu":
            return self.handle_menu(input)

        raise ValueError("Invalid action: '%s'" % self.current_action)

    def setup(self, user) -> tuple[str, str]:
        return self.get_menu(), [str(i + 1) for i in range(8)]

    def info(self) -> dict:
        return {"id": "box_pusher", "name": "Box Pusher"}


if __name__ == "__main__":
    ...
