import pygame
import os
import json

level_file = os.path.join(os.path.dirname(__file__), "levels.json")

pygame.init()

# Constants
CELL_SIZE = 50  # Size of each cell
CHARACTERS = [" ", 'B', 'T', 'P', 'R', '#']

# Default values
GRID_WIDTH, GRID_HEIGHT = 10, 10

# Level class to handle individual levels
class Level:
    def __init__(self, width, height, board=None):
        self.width = width
        self.height = height
        if board:
            self.board = [[CHARACTERS.index(cell) for cell in row] for row in board]
        else:
            self.board = [[0] * width for _ in range(height)]

    def draw(self, screen, font):
        for y in range(self.height):
            for x in range(self.width):
                cell_rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (0, 0, 0), cell_rect)  # Draw cell background
                pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)  # Draw cell border

                # Render and draw character
                text_surface = font.render(CHARACTERS[self.board[y][x]], True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=cell_rect.center)
                screen.blit(text_surface, text_rect)

    def count_players(self):
        return sum(row.count(CHARACTERS.index('P')) for row in self.board)

    def find_player_position(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == CHARACTERS.index('P'):
                    return (x, y)
        return None

    def resize(self, delta_width, delta_height):
        if delta_width != 0:
            if delta_width > 0:
                for row in self.board:
                    row.extend([0] * delta_width)
            elif delta_width < 0:
                for row in self.board:
                    for _ in range(-delta_width):
                        if row:
                            row.pop()
            self.width = max(1, self.width + delta_width)

        if delta_height != 0:
            if delta_height > 0:
                for _ in range(delta_height):
                    self.board.append([0] * self.width)
            elif delta_height < 0:
                for _ in range(-delta_height):
                    if self.board:
                        self.board.pop()
            self.height = max(1, self.height + delta_height)

# LevelManager class to handle loading, saving, and switching between levels
class LevelManager:
    def __init__(self, filename):
        self.filename = filename
        self.levels = []
        self.current_level = 0
        self.load_levels()

    def load_levels(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                levels_data = json.load(f)
                self.levels = [Level(level['width'], level['height'], level['board']) for level in levels_data]
        if not self.levels:
            self.create_new_level()

    def save_levels(self):
        levels_data = [{
            'width': level.width,
            'height': level.height,
            'board': [[CHARACTERS[cell] for cell in row] for row in level.board]
        } for level in self.levels]
        with open(self.filename, 'w') as f:
            json.dump(levels_data, f)
        print("Levels saved to", self.filename)  # Debug print

    def create_new_level(self):
        new_level = Level(GRID_WIDTH, GRID_HEIGHT)
        self.levels.append(new_level)
        self.load_level(len(self.levels) - 1)

    def load_level(self, index):
        if 0 <= index < len(self.levels):
            self.current_level = index
            print(f"Level {self.current_level} loaded.")  # Debug print
            return self.levels[index]
        return None

# Game class to handle the main game logic
class Game:
    def __init__(self):
        self.level_manager = LevelManager(level_file)
        self.level = self.level_manager.load_level(0)
        self.font = pygame.font.SysFont(None, CELL_SIZE - 10)
        self.screen = pygame.display.set_mode((self.level.width * CELL_SIZE, self.level.height * CELL_SIZE))

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
            if event.button in [3, 5]:
                new_value = (self.level.board[y][x] - 1) % len(CHARACTERS)
                while CHARACTERS[new_value] == 'P' and self.level.count_players() >= 1:
                    new_value = (new_value - 1) % len(CHARACTERS)
                self.level.board[y][x] = new_value  # Cycle through characters
            else:
                new_value = (self.level.board[y][x] + 1) % len(CHARACTERS)
                while CHARACTERS[new_value] == 'P' and self.level.count_players() >= 1:
                    new_value = (new_value + 1) % len(CHARACTERS)
                self.level.board[y][x] = new_value  # Cycle through characters

    def handle_key_press(self, event):
        key = event.unicode.upper()
        x, y = pygame.mouse.get_pos()
        x //= CELL_SIZE
        y //= CELL_SIZE
        if 0 <= x < self.level.width and 0 <= y < self.level.height:
            if key in CHARACTERS:
                new_value = CHARACTERS.index(key)
                if CHARACTERS[new_value] == 'P':
                    current_player_position = self.level.find_player_position()
                    if current_player_position:
                        px, py = current_player_position
                        self.level.board[py][px] = CHARACTERS.index(' ')  # Remove current player
                self.level.board[y][x] = new_value
            elif key.isdigit():
                new_value = int(key) % len(CHARACTERS)
                if CHARACTERS[new_value] == 'P':
                    current_player_position = self.level.find_player_position()
                    if current_player_position:
                        px, py = current_player_position
                        self.level.board[py][px] = CHARACTERS.index(' ')  # Remove current player
                self.level.board[y][x] = new_value
        if key == '+':  # Next level
            self.level = self.level_manager.load_level((self.level_manager.current_level + 1) % len(self.level_manager.levels))
            self.update_screen_size()
        elif key == '-':  # Previous level
            self.level = self.level_manager.load_level((self.level_manager.current_level - 1) % len(self.level_manager.levels))
            self.update_screen_size()
        elif key == 'N':  # Create new level
            self.level_manager.create_new_level()
            self.level = self.level_manager.load_level(len(self.level_manager.levels) - 1)
            self.update_screen_size()

        # Resize level
        if key == 'W':
            self.level.resize(0, -1)  # Remove row from bottom
        elif key == 'A':
            self.level.resize(-1, 0)  # Remove column from right
        elif key == 'S':
            self.level.resize(0, 1)  # Add row to bottom
        elif key == 'D':
            self.level.resize(1, 0)  # Add column to right
        elif event.key == pygame.K_UP:
            self.level.resize(0, -1)  # Remove row from bottom
        elif event.key == pygame.K_DOWN:
            self.level.resize(0, 1)  # Add row to bottom
        elif event.key == pygame.K_LEFT:
            self.level.resize(-1, 0)  # Remove column from right
        elif event.key == pygame.K_RIGHT:
            self.level.resize(1, 0)  # Add column to right

        self.update_screen_size()

    def update_screen_size(self):
        self.screen = pygame.display.set_mode((self.level.width * CELL_SIZE, self.level.height * CELL_SIZE))

# Initialize and run the game
game = Game()
game.run()
