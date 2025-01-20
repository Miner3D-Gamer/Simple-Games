from typing import Literal, Dict, Union, Iterable, Tuple, List,Any,Optional

import json, os
from copy import deepcopy as copy
from tge.manipulation.list_utils import decompress_list_of_lists
import ijson


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
        self.worlds_per_page = 6

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
            metadata: Dict[str, Any] = {}
            current_key = ""
            current_object:Union[Dict[str, Any], List[Any]] = metadata

            for prefix, event, value in parser:
                if found:
                    if event == "map_key":
                        current_key = value
                    elif event in ("start_map", "start_array"):
                        new_object:Union[Dict[str, Any], List[Any]] = {} if event == "start_map" else []
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

    def generate_menu(self, options: list[str], width: int, title: str = "") -> str:
        menu = []
        min_buffer = 2

        for i in range(len(options) + 1):  # "⬅⬆⬇➡"
            new = len([*options, title][i]) + 4 + min_buffer * 2
            if new > width:
                width = new

        border = self.format_string("", width, "#", min_buffer)
        menu.append(border)
        if title:
            menu.append(self.format_string(" %s " % title, width, "#", min_buffer))
            menu.append(border)

        for i in range(len(options)):  # "⬅⬆⬇➡"
            menu.append(
                self.format_string(
                    " %s %s " % (i + 1, options[i]), width, "#", min_buffer
                )
            )
        menu.append(border)
        return ("\n".join(menu)).replace("#", "█")

    def get_menu(self):
        menu_width = 10
        if self.menu_id == "main":
            return self.generate_menu(
                ["Play", "Settings", "Info", "Exit"], menu_width, "Main Menu"
            )
        elif self.menu_id == "settings":
            return self.generate_menu(
                [
                    "Main Menu",
                    "Change Menu Style",
                    "Not implemented",
                    "Not implemented",
                ],
                menu_width,
                "Settings",
            )
        elif self.menu_id == "world_selection":
            return self.generate_menu(
                ["Main menu", "Next Page"]
                + [
                    "World: " + _
                    for _ in self.get_world_names_for_page(
                        self.current_world_selection_page, self.worlds_per_page
                    )
                ]
                + ["Previous Page"],
                menu_width,
                "World Selection (%s / %s)"
                % (
                    self.current_world_selection_page + 1,
                    self.get_total_world_pages(self.worlds_per_page),
                ),
            )
        elif self.menu_id == "info":
            return self.generate_menu(
                ["Main Menu", "Not implemented", "Not implemented", "Not implemented"],
                menu_width,
                "Info",
            )
        elif self.menu_id == "change_menu_style":
            return self.generate_menu(
                [
                    "Back to settings",
                    "Text padding: left",
                    "Text padding: middle",
                    "Text padding: right",
                ],
                menu_width,
                "Change Menu Style",
            )

        return "Invalid menu ID (Generating Menu): %s" % self.menu_id

    def get_world_names_for_page(self, page: int, page_size: int = 10) -> list[str]:
        return self.get_all_world_names()[page * page_size : (page + 1) * page_size]

    def get_world_from_page_and_index(
        self, page: int, index: int, page_size: int = 10
    ) -> str:
        global_index = page * page_size + index

        all_world_names = self.get_all_world_names()

        if 0 <= global_index < len(all_world_names):
            return all_world_names[global_index]
        else:
            raise IndexError("Invalid page or index")

    def get_total_world_pages(self, page_size: int = 10) -> int:
        total_world_names = len(self.get_all_world_names())
        if page_size <= 0:
            raise ValueError("Page size must be greater than zero.")
        return (total_world_names + page_size - 1) // page_size

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

    def get_all_world_files(self) -> list[str]:

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
            return [""]

    def get_level(self, world: str, level: str):

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
                elif cell == "H":
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
            new_id = self.get_id_at(new_coords)
            print(new_id, id)
            if new_char == char and new_id == id:
                self.destroy_all_connected(new_coords)

    def spawn_secret(self, coords: tuple[int, int]):
        x, y = coords
        if self.get_item_at((x, y)) == " ":
            self.board[y][x] = "H"
            return True
        return False

    def spawn_reset_button(self, coords: tuple[int, int]):
        x, y = coords
        if self.get_item_at((x, y)) == " ":
            self.board[y][x] = "R"
            return True
        return False

    def start_round(self, world: str) -> Optional[bool]:
        self.player_exists = False

        data = self.get_level(world, str(self.level_id))
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

    def get_id_at(self, coords: tuple[int, int]) -> int:
        if not self.is_in_bounce(coords):
            return -1
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

    def sign(self, num: int) -> Literal[1] | Literal[-1] | Literal[0]:
        return 1 if num > 0 else -1 if num < 0 else 0

    def move_by(self, current_x, current_y, offset_x, offset_y):

        current_item: str = self.board[current_y][current_x]
        target_x = current_x + offset_x
        target_y = current_y + offset_y
        item = self.get_item_at((target_x, target_y))
        if item in ["#", "b"]:
            return False
        if item == "B":
            successful = self.move_by(
                target_x, target_y, self.sign(offset_x), self.sign(offset_y)
            )
            if not successful:
                return False
        if item == "H":
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
        if isinstance(exits, dict):
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
        if isinstance(exits, str):
            return exits, False
        if isinstance(exits, list):
            raise NotImplementedError("Optional level selection not implemented")
        if isinstance(exits, int):
            return metadata["level_order"][exits], False
        if exits is None:
            return "", True
        raise ValueError("Unrecognized exit type")

    def world_name_to_file(self, name: str) -> str:
        world_names = self.get_all_world_names()
        return self.get_all_world_files()[world_names.index(name)]

    def change_menu(self, menu_id: str):
        self.current_action = "menu"
        self.menu_id = menu_id
        return {"frame": self.get_menu()}

    def handle_menu(self, input: int):

        play = lambda: self.change_menu("world_selection")
        settings = lambda: self.change_menu("settings")
        main_menu = lambda: self.change_menu("main")
        change_menu_style = lambda: self.change_menu("change_menu_style")

        def not_yet_implemented():
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
            pages = self.get_total_world_pages(self.worlds_per_page)
            if self.current_world_selection_page < 0:
                self.current_world_selection_page = (
                    pages + 1
                ) - self.current_world_selection_page
            self.current_world_selection_page %= pages
            return {"frame": self.get_menu()}

        world_selection_next_page = lambda: change_world_selection_page(1)
        world_selection_previous_page = lambda: change_world_selection_page(-1)

        def selected_world():
            world = self.get_world_from_page_and_index(
                self.current_world_selection_page, input - 2, self.worlds_per_page
            )
            self.current_world = self.world_name_to_file(world)
            return start()

        def change_menu_style_internal(new: Literal["left", "right", "center"]):
            self.formatting = new
            return {"frame": self.get_menu()}

        change_menu_style_to_left = lambda: change_menu_style_internal("left")
        change_menu_style_to_right = lambda: change_menu_style_internal("right")
        change_menu_style_to_center = lambda: change_menu_style_internal("center")

        info = lambda: self.change_menu("info")

        happenings = {
            "main": [play, settings, info, exit],
            "settings": [
                main_menu,
                change_menu_style,
                not_yet_implemented,
                not_yet_implemented,
            ],
            "world_selection": [
                main_menu,
                world_selection_next_page,
                *[selected_world] * len(self.get_all_world_files()),
                world_selection_previous_page,
            ],
            "info": [
                main_menu,
                not_yet_implemented,
                not_yet_implemented,
                not_yet_implemented,
            ],
            "change_menu_style": [
                settings,
                change_menu_style_to_left,
                change_menu_style_to_center,
                change_menu_style_to_right,
            ],
        }
        pass_func = lambda: {
            "frame": "Invalid menu ID (Menu Handler): %s" % self.menu_id,
            "action": "end",
        }
        try:
            func = happenings.get(self.menu_id, [pass_func] * 4)[input]
        except IndexError:
            return pass_func()

        return func()

    def exit_world(self):
        next = self.change_menu("world_selection")
        next.update({"action": "change_inputs", "inputs": "range-1-4"})
        return next

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
                    return self.exit_world()
                if not self.level_id:
                    raise BaseException(
                        "Invalid level id to load: '%s' loaded with id %s in level '%s'"
                        % (self.level_id, self.get_last_player_id(), last_level_id)
                    )
                not_done = self.start_round(self.current_world)
                if not not_done:
                    if not_done is None:
                        return None
                    return self.exit_world()

            return {"frame": self.get_board()}
        elif self.current_action == "menu":
            return self.handle_menu(input)

        raise ValueError("Invalid action: '%s'" % self.current_action)

    def setup(self, info: Dict[
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
        ],) -> Tuple[
        str,
        Union[
            Iterable,
            Literal["arrows", "range-{min}-{max}"],
        ],
        Optional[Dict[Literal["receive_last_frame"], bool]],
    ]:
        return self.get_menu(), "range-1-4", None

    def info(self) -> dict:
        return {
            "id": "box_pusher",
            "name": "Box Pusher",
            "description": "A simple puzzle game",
        }


if __name__ == "__main__":
    ...
