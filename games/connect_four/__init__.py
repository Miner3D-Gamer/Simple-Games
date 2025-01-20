import os
os.system("cls")
size = (7, 6)

board = []
for i in range(size[0]):
    _ = []
    for j in range(size[1]):
        _.append(None)#j * size[1] + i)
    board.append(_)


def y_x_to_id(y, x, width):
    return y * width + x


def id_to_y_x(id, width):
    return id // width, id % width

def visualize():
    for x in range(size[1]):
        for y in range(size[0]):
            char = board[y][x]
            print(char if not char is None else " ", end=" ")
        #y,x=id_to_y_x(i, size[0])
        
        print()

def get_lowest_in_row(x):
    l = len(board[x]) 
    for i in range(l):
        if not board[x][i] is None:
            return i -1
    return i

def place_in_row(row, char):
    global board
    y = get_lowest_in_row(row)
    if y < 0:
        return False
    board[row][y] = char
    won = check_for_win_condition_at_x_y(y, row, board, char)
    if won:
        return None
    return True

def visualize_cursor(x):
    before = x
    after = size[0]-x-1
    string = "-" * before + "V" + "-" * after
    print("".join([x + " " for x in string]))

def os_in_bounce(x, y):
    return x >= 0 and x < size[1] and y >= 0 and y < size[0]


def _check_for_win_condition_horizontal(x, y, things, win_char, wind_length):
    for i in range(wind_length):
        if not os_in_bounce(x + i, y):
            return False
        if things[y][x + i] != win_char:
            return False
    return True


def _check_for_win_condition_vertical(x, y, things, win_char, wind_length):
    for i in range(wind_length):
        if not os_in_bounce(x, y + i):
            return False
        if things[y + i][x] != win_char:
            return False
    return True


def _check_for_win_condition_rise(x, y, things, win_char, wind_length):
    for i in range(wind_length):
        if not os_in_bounce(x + i, y - i):
            return False
        if things[y - i][x + i] != win_char:
            return False
    return True


def _check_for_win_condition_fall(x, y, things, win_char, wind_length):
    for i in range(wind_length):
        if not os_in_bounce(x + i, y + i):
            return False
        if things[y + i][x + i] != win_char:
            return False
    return True


def check_for_win_condition_at_x_y(x, y, things:list[list[str]], player):
    length = 4
    ####
    if _check_for_win_condition_horizontal(x, y, things, player, length):
        return True
    if _check_for_win_condition_horizontal(x - length + 1, y, things, player, length):
        return True

    #
    #
    #
    #
    if _check_for_win_condition_vertical(x, y, things, player, length):
        return True
    if _check_for_win_condition_vertical(x, y - length + 1, things, player, length):
        return True

          #
        #
      #
    #
    if _check_for_win_condition_rise(x, y, things, player, length):
        return True
    if _check_for_win_condition_rise(
        x - length + 1, y + length - 1, things, player, length
    ):
        return True

    #
      #
        #
          #
    if _check_for_win_condition_fall(x, y, things, player, length):
        return True
    if _check_for_win_condition_fall(
        x - length + 1, y - length + 1, things, player, length
    ):
        return True
    return False

# cursor = 0
# player = True
# while True:
    
#     while True:
#         os.system("cls")
#         visualize_cursor(cursor)
#         visualize()
#         thing = input()
#         if thing == "a":
#             cursor -= 1
#             if cursor < 0:
#                 cursor = 0
            
#         elif thing == "d":
#             cursor += 1
#             if cursor > size[0] - 1:
#                 cursor = size[0] - 1
#         elif thing == "s":
#             break
            
#     worked = place_in_row(cursor, "X" if player else "O")
    
#     if worked:
#         player = not player
#     if worked is None:
#         print("You won!")
#         break
