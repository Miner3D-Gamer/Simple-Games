from typing import Literal, Dict, Union, Iterable, Tuple, Optional, Any
import os
import random


class Layer:
    def __init__(self, width: int, height: int, data: list["Object"]) -> None:
        self.data = data
        self.width = width
        self.height = height

    def __repr__(self) -> str:
        final = ""
        for x in range(len(self.data)):
            final += object_to_string(self.data[x])
            if (x + 1) % self.width == 0:
                final += "\n"
        return final[:-1]


class Object:
    def __init__(self, type: str, representative: str, solid: bool) -> None:
        self.type = type
        self.representative = representative
        self.solid = solid

    def __repr__(self) -> str:
        return self.representative


class Camera:
    def __init__(self, x: int, y: int, z: int, width_x: int, width_z: int, height_y: int) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.width_x = width_x
        self.width_z = width_z
        self.height_y = height_y

    def move_x(self, x: int):
        self.x += x

    def move_y(self, y: int):
        self.y += y


def get_camera_view_horizontal(
    world: list[Layer], camera: Camera, depth3d: int = 0
) -> tuple[list[Any], list[Any]]:

    if camera.z < 0:
        current = world[0]
    elif camera.z >= len(world):
        current = world[-1]
    else:
        current = world[camera.z]

    def clamp_view(cam_pos: int, cam_size: int, max_size: int) -> tuple[int, int]:
        """Calculate start and end positions for a given dimension."""
        start = max(0, min(cam_pos, max_size - cam_size))
        end = min(max_size, start + cam_size)
        return start, end

    x_start, x_end = clamp_view(camera.x, camera.width_x, current.width)
    y_start, y_end = clamp_view(camera.y, camera.width_z, current.height)
    view = []
    for y in range(y_start, y_end):
        for x in range(x_start, x_end):
            view.append(current.data[x + y * current.width])

    if False and camera.z > 0 and depth3d < camera.height_y//2 and any([x.type == " " for x in view]):
        below_view, depth = get_camera_view_horizontal(
            world,
            Camera(camera.x, camera.y, camera.z - 1, camera.width_x, camera.width_z, camera.width_z),
            depth3d=depth3d + 1,
        )
        with open("test.txt" + str(camera.z - 1), "w") as f:
            f.write(Layer(camera.width_x, camera.width_z, below_view).__repr__())

        idx = 0
        for i in view:
            if i.type == " ":
                continue

            below_view[idx] = i
            depth[idx] = camera.z
            idx += 1
        return below_view, depth

    depth = [camera.z for _ in range(len(view))]

    return view, depth


def unroll_2d_list(lst: list[list[Any]]) -> list[Any]:
    return [item for sublist in lst for item in sublist]


def object_to_string(obj: Object) -> str:
    return obj.representative


def color_string(string: str, color: tuple[int, int, int]):
    return f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m{string}\x1b[0m"


def slice_to_output(slice: list[Object], depth: list[int], cam: Camera, world) -> str:
    with open("test.txt", "w") as f:
        for x in range(len(slice)):
            f.write(slice[x].representative)
            if (x + 1) % cam.width_x == 0:
                f.write("\n")
        f.write("\n")
        for x in range(len(slice)):
            f.write(str(depth[x]))
            if (x + 1) % cam.width_x == 0:
                f.write("\n")
        f.write("\n")
        f.write("\n".join([str(x) + "\n---\n" for x in world]))
    rt = ""

    for x in range(len(slice)):
        rt += color_string(
            object_to_string(slice[x]),
            (
                255 // ((cam.z - depth[x]) + 1),
                255 // ((cam.z - depth[x]) + 1),
                255 // ((cam.z - depth[x]) + 1),
            ),
        )
        if (x + 1) % cam.width_x == 0:
            rt += "\n"
    return rt[:-1]


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
                Optional[Union[Iterable[str], Literal["arrows", "range-{min}-{max}"]]],
            ],
        ],
    ]:
        """
        A function called for every frame

        None: Something went wrong yet instead of raising an error, None can be returned to signalize that the game loop should be stopped

        Actions:
            "end": Displays the last frame and ends the game loop

            "change_inputs": Requires another variable neighboring 'actions'; 'inputs'. Changes the inputs if possible

            "error": Displays the given frame yet also signalized that something went wrong

        """
        if input == 0:
            self.cam.x -= 1
        elif input == 1:
            self.cam.y -= 1
        elif input == 2:
            self.cam.y += 1
        elif input == 3:
            self.cam.x += 1
        elif input == 4:
            self.cam.z -= 1
        elif input == 5:
            self.cam.z += 1

        view, depth = get_camera_view_horizontal(self.world, self.cam)

        return {
            "frame": slice_to_output(view, depth, self.cam, self.world)
            + f"\n{input} {self.cam.x} {self.cam.y} {self.cam.z}"
        }

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
            Literal["arrows", "{min}-{max}"],
        ],
        Optional[Dict[Literal["receive_last_frame"], bool]],
    ]:
        width = 20

        self.world = [
            Layer(
                width,
                width,
                unroll_2d_list(
                    [
                        [
                            (
                                Object("Static", " ", False)
                                if random.random() > 0.1
                                else Object("Static", "#", True)
                            )
                            for x in range(width)
                        ]
                        for y in range(width)
                    ]
                ),
            )
            for i in range(width)
        ]
        self.current_world_selection_page = 0
        self.current_world = ""
        self.worlds_per_page = 6
        self.worlds_folder = os.path.dirname(__file__) + "/worlds"
        self.cam = Camera(0, 0, 1, 7, 7, 7)

        self.formatting = "left"
        # self.change_menu("main").popitem()[1]
        return (self.main(2, "").pop("frame")[1], {"presets": "arrows", "custom": ["q", "e"]}, None)  # type: ignore

    def info(self) -> Dict[Literal["name", "id", "description"], str]:
        "Before the game is run, this function is called when adding the game to the library in order to give the user a preview of what's to expect"
        return {
            "name": "Custom game",
            "id": "example_game",
            "description": "A simple game",
        }

    #### Menu Stuff ####

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
            return {
                "frame": "Selected world.",
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

        def selected_world():
            world = self.get_world_from_page_and_index(
                self.current_world_selection_page, input - 2, self.worlds_per_page
            )
            self.current_world = self.world_name_to_file(world)
            return start()

        def change_menu_style_internal(new: Literal["left", "right", "center"]):
            self.formatting = new
            return {"frame": self.get_menu()}

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
                lambda: change_world_selection_page(1),
                *[selected_world] * len(self.get_all_world_files()),
                lambda: change_world_selection_page(-1),
            ],
            "info": [
                main_menu,
                not_yet_implemented,
                not_yet_implemented,
                not_yet_implemented,
            ],
            "change_menu_style": [
                settings,
                lambda: change_menu_style_internal("left"),
                lambda: change_menu_style_internal("center"),
                lambda: change_menu_style_internal("right"),
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

    def get_world_names_for_page(self, page: int, page_size: int = 10) -> list[str]:
        return self.get_all_world_names()[page * page_size : (page + 1) * page_size]

    ##### World Loading ######
    def get_total_world_pages(self, page_size: int = 10) -> int:
        total_world_names = len(self.get_all_world_names())
        if page_size <= 0:
            raise ValueError("Page size must be greater than zero.")
        return (total_world_names + page_size - 1) // page_size

    def get_all_world_names(self) -> list[str]:
        files = self.get_all_world_files()
        names = []
        for file in files:
            metadata = {}  # self.get_metadata(os.path.join(self.worlds_folder, file))
            name = metadata.get("name", "")
            if not name or not isinstance(name, str):
                name = os.path.splitext(file)[0]
            names.append(name)
        return names

    def get_all_world_files(self) -> list[str]:

        json_files = [f for f in os.listdir(self.worlds_folder) if f.endswith(".json")]

        return sorted(json_files)

    def get_world_from_page_and_index(
        self, page: int, index: int, page_size: int = 10
    ) -> str:
        global_index = page * page_size + index

        all_world_names = self.get_all_world_names()

        if 0 <= global_index < len(all_world_names):
            return all_world_names[global_index]
        else:
            raise IndexError("Invalid page or index")

    def world_name_to_file(self, name: str) -> str:
        world_names = self.get_all_world_names()
        return self.get_all_world_files()[world_names.index(name)]
