from math import log
from typing import Literal
class Game:
    def __init__(self, width: int = 15, height: int = 10, boarder: str = "#") -> None:
        self.level = 5
        self.start_round()
        self.spawn_player(1, 1)
        self.spawn_box(3, 1)
        self.spawn_trigger_pad(4, 1)
        self.spawn_trigger_pad(4, 3)
        self.boarder = boarder
    
    def start_round(self)->None:
        width = int(self.level**1.5)
        self.generate_board(width, int(width*0.8))

    def generate_board(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        board = []
        local_board = []
        for y in range(height):
            board.append([" "] * width)
        self.board: list[list[str]] = board
    
    def spawn_wall(self, x:int, y:int)->bool:
        if  self.get_item_at(x, y) == " ":
            self.board[y][x] = "#"
            return True
        return False
    
    def spawn_trigger_pad(self, x:int, y:int)->bool:
        if  self.get_item_at(x, y) == " ":
            self.board[y][x] = "T"
            return True
        return False
    
    def spawn_box(self, x:int, y:int)->bool:
        if  self.get_item_at(x, y) == " ":
            self.board[y][x] = "B"
            return True
        return False

    def spawn_player(self, x:int, y:int)->bool:
        
        if not self.get_item_at(x, y) == "#":
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
    
    def is_board_been_completed(self)->bool: #engrish
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

    def move(self, direction: int)->None:
        if direction == 0: # Left
            self.move_by(self.pos_x, self.pos_y, -1, 0)
        elif direction == 1: # Up
            self.move_by(self.pos_x, self.pos_y, 0, -1)
        elif direction == 2: # Down
            self.move_by(self.pos_x, self.pos_y, 0, 1)
        elif direction == 3: # Right
            self.move_by(self.pos_x, self.pos_y, 1, 0)
    
    def minimize(self, num:int)->Literal[1]|Literal[-1]:
        return num//abs(num)

    def move_by(self, current_x, current_y, offset_x, offset_y):
        
        current_item:str = self.board[current_y][current_x]
        target_x = current_x + offset_x
        target_y =current_y + offset_y
        item = self.get_item_at(target_x, target_y)
        if item in ["#", "b"]:
            return False
        if item == "B":
            successful = self.move_by(target_x, target_y, self.minimize(offset_x) if offset_x!=0 else 0, self.minimize(offset_y) if offset_y!=0 else 0)
            if not successful:
                return False
        
        if item == "T":
            self.board[target_y][target_x] = current_item.lower()
        else:
            self.board[target_y][target_x] = current_item.upper()
        
        self.board[current_y][current_x] = " " if current_item.isupper() else "T"
        
        if current_item.upper() == "P":
            self.pos_x, self.pos_y = target_x, target_y
        return True

    def main(self, input: int, user:str) -> None | str | list:
        if not (input > -1 and input < 4):
            return None
        self.move(input)
        done = self.is_board_been_completed()
        if done:
            return [self.get_board() + "\nBoard is Completed"]
        return self.get_board()

    def setup(self, user) -> str:
        return self.get_board()
    
    def info(self)->list[str,str, list[str] | str]:
        return ["box_pusher", "Box Pusher", "arrows"]
