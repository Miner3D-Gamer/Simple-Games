import pygame
import os
import json
from tge.manipulation.list_utils import decompress_list_of_lists, compress_list_of_lists
import random
from copy import deepcopy as copy

level_file = os.path.join(os.path.dirname(__file__), "worlds", "builtin.json")


def get_new_level_name(name_length: int = 10) -> str:
    return "".join(
        [
            random.choice(
                "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
            )
            for i in range(name_length)
        ]
    )


pygame.init()

# Constants
CELL_SIZE = 50  # Size of each cell
CHARACTERS = [i.upper() for i in [" ", "B", "T", "H", "F", "P", "R", "C", "#"]]
CHARACTERS.extend([i.lower() for i in CHARACTERS])
print(CHARACTERS)


# Add menus
# Level Editor - Done

#   - Air
# # - Wall
# B - Box
# T - Trigger
# H - Hidden
# P - Player (Spawn)
# R - Reset


## ALL FOLLOWING FEATURES ARE NOT IMPLEMENTED:
# C - Coin
# F - Force Reposition
# E - Explosive
# S - Spikes
# M - Moving
# D - Door
# I - Interact (Button)

# camera types:
# fixed
# follow
# follow_horizontally
# follow_vertically
# offset

# Default values
GRID_WIDTH, GRID_HEIGHT = 10, 8


# Level class to handle individual levels
class Level:
    def __init__(self, width, height, board=None, id_board=None, metadata=None):
        self.width = width
        self.height = height
        self.metadata = metadata or {
            "title": "",
            "description": "",
            "difficulty": "",
            "continue_condition": {"condition": "hit_trigger_all"},
            "visual_overwrites": {},
            "exits": {},
            "force_exists": {},
            "camera": {"type": "fixed", "offset": (0, 0), "view_range": "full"},
        }
        if board:
            self.board = [[CHARACTERS.index(cell) for cell in row] for row in board]
        else:
            self.board = [[0] * width for _ in range(height)]

        if id_board:
            self.id_board: list[list[int]] = id_board
        else:
            self.id_board: list[list[int]] = [[0] * width for _ in range(height)]

    def draw(self, screen, font):
        for y in range(self.height):
            for x in range(self.width):
                cell_rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, (0, 0, 0), cell_rect)  # Draw cell background
                pygame.draw.rect(
                    screen, (255, 255, 255), cell_rect, 1
                )  # Draw cell border

                # Render and draw character
                text_surface = font.render(
                    CHARACTERS[self.board[y][x]], True, (255, 255, 255)
                )
                text_rect = text_surface.get_rect(center=cell_rect.center)
                screen.blit(text_surface, text_rect)

                # Render and draw ID if it exists
                if int(self.id_board[y][x]) != 0:
                    id_surface = font.render(
                        str(self.id_board[y][x]), True, (255, 255, 255)
                    )
                    id_rect = id_surface.get_rect(bottomright=cell_rect.bottomright)
                    screen.blit(id_surface, id_rect)

    def count_players(self):
        return sum(row.count(CHARACTERS.index("P")) for row in self.board)

    def find_player_position(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == CHARACTERS.index("P"):
                    return (x, y)
        return None

    def resize(self, delta_width, delta_height):
        # Handle horizontal resizing
        if delta_width > 0:
            for row in self.board:
                row.extend([0] * delta_width)
            for row in self.id_board:
                row.extend([0] * delta_width)
        elif delta_width < 0:
            for row in self.board:
                for _ in range(-delta_width):
                    if row:
                        row.pop()
            for row in self.id_board:
                for _ in range(-delta_width):
                    if row:
                        row.pop()
        self.width = max(1, self.width + delta_width)

        # Handle vertical resizing
        if delta_height > 0:
            for _ in range(delta_height):
                self.board.append([0] * self.width)
                self.id_board.append([0] * self.width)
        elif delta_height < 0:
            for _ in range(-delta_height):
                if self.board:
                    self.board.pop()
                if self.id_board:
                    self.id_board.pop()
        self.height = max(1, self.height + delta_height)

    def expand_and_shift(self, delta_width, delta_height):
        # Handle leftward expansion
        if delta_width < 0:
            for row in self.board:
                for _ in range(-delta_width):
                    row.insert(0, 0)
            for row in self.id_board:
                for _ in range(-delta_width):
                    row.insert(0, 0)
            self.width += -delta_width
        elif delta_width > 0:
            for row in self.board:
                row.extend([0] * delta_width)
            for row in self.id_board:
                row.extend([0] * delta_width)
            self.width += delta_width

        # Handle upward expansion
        if delta_height < 0:
            for _ in range(-delta_height):
                self.board.insert(0, [0] * self.width)
                self.id_board.insert(0, [0] * self.width)
            self.height += -delta_height
        elif delta_height > 0:
            for _ in range(delta_height):
                self.board.append([0] * self.width)
                self.id_board.append([0] * self.width)
            self.height += delta_height

    def shrink_and_shift(self, delta_width, delta_height):
        # Handle leftward shrinking
        if delta_width > 0:
            for row in self.board:
                for _ in range(delta_width):
                    if row:
                        row.pop(0)
            for row in self.id_board:
                for _ in range(delta_width):
                    if row:
                        row.pop(0)
            self.width = max(1, self.width - delta_width)
        # Handle rightward expanding
        elif delta_width < 0:
            for row in self.board:
                for _ in range(-delta_width):
                    row.insert(0, 0)  # Assuming None as a placeholder for new cells
            for row in self.id_board:
                for _ in range(-delta_width):
                    row.insert(0, 0)
            self.width += -delta_width

        # Handle upward shrinking
        if delta_height > 0:
            for _ in range(delta_height):
                if self.board:
                    self.board.pop(0)
                if self.id_board:
                    self.id_board.pop(0)
            self.height = max(1, self.height - delta_height)
        # Handle downward expanding
        elif delta_height < 0:
            for _ in range(-delta_height):
                self.board.insert(
                    0, [0] * self.width
                )  # Assuming None as a placeholder for new cells
                self.id_board.insert(0, [0] * self.width)
            self.height += -delta_height

    def all_players_have_id(self):
        for y in range(self.height):
            for x in range(self.width):
                if (
                    self.board[y][x] == CHARACTERS.index("P")
                    and self.id_board[y][x] is None
                ):
                    return False
        return True


# LevelManager class to handle loading, saving, and switching between levels
class LevelManager:
    def __init__(self, filename):
        self.filename = filename
        self.levels = {}  # Store levels by name
        self.world_metadata = {}
        self.level_order = []  # Store the order of levels by their names
        self.current_level_id = 0
        self.load_levels()

    def load_levels(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                levels_data: dict = json.load(f)
                self.world_metadata: dict = levels_data.get("metadata", {})
                self.world_name = levels_data.get("name", "New World")
                self.world_description = levels_data.get("description", "")
                self.level_order: list[str] = self.world_metadata.get("level_order", [])

                # Load levels from the "levels" dictionary
                levels_dict: dict[str, dict] = levels_data.get("levels", {})
                for level_name in self.level_order:
                    level_data = levels_dict.get(level_name)
                    if level_data:
                        self.levels[level_name] = Level(
                            level_data["width"],
                            level_data["height"],
                            decompress_list_of_lists(
                                level_data["board"], level_data["width"]
                            ),
                            decompress_list_of_lists(
                                level_data.get("id_board"), level_data["width"]
                            ),
                            level_data.get("metadata", {}),
                        )

                # Ensure all levels are in the level order
                for level_name in levels_dict.keys():
                    if level_name == "" or level_name.isdigit():
                        level_name = "invalid_level_name_" + get_new_level_name(10)
                    if level_name not in self.level_order:
                        self.level_order.append(level_name)
                        self.levels[level_name] = Level(
                            levels_dict[level_name]["width"],
                            levels_dict[level_name]["height"],
                            decompress_list_of_lists(
                                levels_dict[level_name]["board"],
                                levels_dict[level_name]["width"],
                            ),
                            decompress_list_of_lists(
                                levels_dict[level_name].get("id_board"),
                                levels_dict[level_name]["width"],
                            ),
                            levels_dict[level_name].get("metadata", {}),
                        )

                # Optionally, save updated level_order back to the file
                self.world_metadata["level_order"] = self.level_order
                levels_data["metadata"] = self.world_metadata
                with open(self.filename, "w") as f:
                    json.dump(levels_data, f, indent=4)

        # Create a new level if no levels are loaded
        if not self.level_order:
            self.create_new_level()

    def save_levels(self):
        self.world_metadata["level_order"] = self.level_order
        self.world_metadata["name"] = self.world_name
        self.world_metadata["description"] = self.world_description
        levels_data = {
            "metadata": self.world_metadata,
            "levels": {},  # Initialize an empty dictionary for levels
        }

        # Save each level under its name in the "levels" dictionary
        for level_name in self.level_order:
            level = self.levels[level_name]
            levels_data["levels"][level_name] = {
                "width": level.width,
                "height": level.height,
                "board": compress_list_of_lists(
                    [[CHARACTERS[cell] for cell in row] for row in level.board]
                ),
                "id_board": compress_list_of_lists(
                    [
                        [
                            str(item) if isinstance(item, int) else item
                            for item in sub_id_list
                        ]
                        for sub_id_list in level.id_board
                    ]
                ),
                "metadata": level.metadata,
            }

        with open(self.filename, "w") as f:
            json.dump(levels_data, f)
        print("Levels saved to", self.filename)  # Debug print

    def create_new_level(self, name="New Level"):
        new_level = Level(GRID_WIDTH, GRID_HEIGHT)
        self.levels[name] = new_level
        self.level_order.append(name)
        self.load_level(len(self.level_order) - 1)

    def load_level(self, level_name: str) -> None | Level:
        """Load a level by its name."""
        if level_name in self.level_order:
            self.current_level_id = self.level_order.index(level_name)
            print(f"Level {level_name} loaded.")  # Debug print
            return self.levels[level_name]
        else:
            print(f"Level {level_name} not found.")  # Debug print
            return None

    def delete_level(self, index):
        if 0 <= index < len(self.level_order):
            level_name = self.level_order.pop(index)
            deleted_level = self.levels.pop(level_name)

            # Adjust current_level if necessary
            if self.current_level_id >= len(self.level_order):
                self.current_level_id = len(self.level_order) - 1
            elif self.current_level_id > index:
                self.current_level_id -= 1

            # Save changes
            self.save_levels()
            print(f"Level {level_name} deleted.")  # Debug print
            return deleted_level
        else:
            print("Invalid level index. No level deleted.")  # Debug print
            return None


def is_character_valid_for_id(char: str) -> bool:
    return char.upper() != char.lower()


# Game class to handle the main game logic
class Game:
    def __init__(self):
        self.level_manager = LevelManager(level_file)
        self.level = self.level_manager.load_level(
            next(iter(self.level_manager.levels), None)
        )
        self.font = pygame.font.SysFont(None, CELL_SIZE - 10)
        self.screen = pygame.display.set_mode(
            (self.level.width * CELL_SIZE, self.level.height * CELL_SIZE)
        )

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_press(event)

            self.screen.fill((0, 0, 0))
            self.level.draw(self.screen, self.font)
            pygame.display.flip()

        self.level_manager.save_levels()
        pygame.quit()

    def handle_mouse_click(self, event):
        x, y = pygame.mouse.get_pos()
        x //= CELL_SIZE
        y //= CELL_SIZE
        if 0 <= x < self.level.width and 0 <= y < self.level.height:
            if event.button == 2:
                new_value = (self.level.board[y][x] + (len(CHARACTERS) // 2)) % (
                    len(CHARACTERS)
                )
                self.level.board[y][x] = new_value
            elif event.button in [3, 5]:
                new_value = (self.level.board[y][x] - 1) % (len(CHARACTERS) // 2)
                while (
                    CHARACTERS[new_value] == "P"
                    and self.level.count_players() >= 1
                    and not self.level.all_players_have_id()
                ):
                    new_value = (new_value - 1) % (len(CHARACTERS) // 2)
                self.level.board[y][x] = new_value
            else:
                new_value = (self.level.board[y][x] + 1) % (len(CHARACTERS) // 2)
                while (
                    CHARACTERS[new_value] == "P"
                    and self.level.count_players() >= 1
                    and not self.level.all_players_have_id()
                ):
                    new_value = (new_value + 1) % (len(CHARACTERS) // 2)
                self.level.board[y][x] = new_value
                if not is_character_valid_for_id(CHARACTERS[new_value]):
                    self.level.id_board[y][x] = 0

    def handle_key_press(self, event: pygame.event.Event):

        key = event.unicode.upper()
        shift_pressed = event.mod == 4097
        x, y = pygame.mouse.get_pos()
        x //= CELL_SIZE
        y //= CELL_SIZE
        if 0 <= x < self.level.width and 0 <= y < self.level.height:
            if key in CHARACTERS:
                new_value = CHARACTERS.index(key)
                if CHARACTERS[new_value] == "P":
                    if (
                        self.level.count_players() >= 1
                        and not self.level.all_players_have_id()
                    ):
                        return
                    current_player_position = self.level.find_player_position()
                    if current_player_position:
                        px, py = current_player_position
                        if self.level.id_board[py][px] is None:
                            self.level.board[py][px] = CHARACTERS.index(" ")
                self.level.board[y][x] = new_value
                if not is_character_valid_for_id(CHARACTERS[new_value]):
                    self.level.id_board[y][x] = 0
            elif key.isdigit():
                if is_character_valid_for_id(CHARACTERS[self.level.board[y][x]]):
                    self.level.id_board[y][x] = int(key)

        if key == "+":
            next_index = (self.level_manager.current_level_id + 1) % len(
                self.level_manager.levels
            )
            self.level = self.level_manager.load_level(
                list(self.level_manager.levels.keys())[next_index]
            )
            self.update_screen_size()
        elif key == "-":
            previous_index = (self.level_manager.current_level_id - 1) % len(
                self.level_manager.levels
            )
            self.level = self.level_manager.load_level(
                list(self.level_manager.levels.keys())[previous_index]
            )
            self.update_screen_size()
        elif key == "N":
            if shift_pressed:
                new_name = f"copied_level_{len(self.level_manager.levels)+1}_{get_new_level_name()}"
                self.level_manager.levels[new_name] = copy(self.level)
                self.level_manager.load_level(new_name)
            else:
                new_name = f"new_level_{len(self.level_manager.levels)+1}_{get_new_level_name()}"
                self.level_manager.create_new_level(new_name)
                self.level = self.level_manager.load_level(new_name)
            self.update_screen_size()

        if key == "W":
            self.level.shrink_and_shift(0, 1)
        elif key == "S":
            self.level.shrink_and_shift(0, -1)
        elif key == "A":
            self.level.shrink_and_shift(1, 0)
        elif key == "D":
            self.level.shrink_and_shift(-1, 0)
        #
        elif event.key == pygame.K_UP:
            self.level.resize(0, -1)
        elif event.key == pygame.K_DOWN:
            self.level.resize(0, 1)
        elif event.key == pygame.K_LEFT:
            self.level.resize(-1, 0)
        elif event.key == pygame.K_RIGHT:
            self.level.resize(1, 0)

        elif event.key == pygame.K_DELETE and shift_pressed:
            self.level_manager.delete_level(self.level_manager.current_level_id)
            if len(self.level_manager.levels) != 0:

                next_index = (self.level_manager.current_level_id + 1) % len(
                    self.level_manager.levels
                )
                self.level = self.level_manager.load_level(
                    list(self.level_manager.levels.keys())[next_index]
                )

            else:
                self.level_manager.create_new_level(
                    f"new_level_{len(self.level_manager.levels)+1}_{get_new_level_name()}"
                )
                next_index = (self.level_manager.current_level_id - 1) % len(
                    self.level_manager.levels
                )
                self.level = self.level_manager.load_level(
                    list(self.level_manager.levels.keys())[next_index]
                )
                self.update_screen_size()

        self.update_screen_size()

    def update_screen_size(self):
        self.screen = pygame.display.set_mode(
            (self.level.width * CELL_SIZE, self.level.height * CELL_SIZE)
        )


# Initialize and run the game
game = Game()
game.run()
