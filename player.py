class Game:
    def __init__(self) -> None: ...
    def main(self, input: int, user: str) -> None | str | list: ...
    def setup(self, user: str) -> str: ...
    def info(self) -> list[str, str, list[str] | str]: ...


import os
import tge
import importlib
from copy import deepcopy

GAMES = {"games": {}}


def load_game(game: Game):

    game = game()

    if not hasattr(game, "info"):
        return "Missing game info"
    if not hasattr(game, "main"):
        return "Missing game mainloop (main)"
    if not hasattr(game, "setup"):
        return "Missing game setup"
    try:
        id, name, inputs = game.info()

    except ValueError as e:
        return "Invalid amount of values received from the info function: %s" % e
    except TypeError as e:
        return "invalid types of value(s) received from the info function: %s" % e
    except Exception as e:
        return "Error in the info function: %s" % e

    if isinstance(inputs, str):
        match inputs:
            case "arrows":

                inputs = [*"⬅⬆⬇➡"]
    elif not tge.tbe.is_iterable(inputs):
        return "Inputs are not iterable"

    if isinstance(inputs, str):
        return "Invalid input preset"
    global GAMES
    GAMES["games"][id] = {}
    GAMES["games"][id]["game"] = game
    GAMES["games"][id]["inputs"] = inputs
    GAMES["games"][id]["name"] = name


current_dir = os.path.dirname(__file__)
for root, dirs, files in os.walk(current_dir, topdown=False):
    if root == current_dir:
        for dir in dirs:
            try:

                game = importlib.import_module(dir)
                if not hasattr(game, "Game"):
                    print("Module %s missing game" % dir)
                    continue
            except Exception as e:
                print("Error while importing %s: %s" % (dir, e))
                continue
            error = load_game(game.Game)
            if error:
                print("Error importing %s:\n%s" % (dir, error))
        else:
            break


def redirect_key(key: str):
    key_translator = {
        "w": "⬆",
        "a": "⬅",
        "s": "⬇",
        "d": "➡",
    }
    return key_translator.get(key, key)


print("\n")

user = tge.file_operations.get_appdata_path()[9:-8]
print(user)
while True:
    while True:
        if len(GAMES["games"]) == 1:
            game_id = [*GAMES["games"]][0]
            break
        print("Select game from this list:")
        print(*GAMES["games"])
        print()
        game = input()
        if not game:
            continue
        if game[0] == "&":
            quit()
        game_id = tge.tbe.strict_autocomplete(game, GAMES["games"])
        if not isinstance(game_id, str):
            tge.console.clear()
            continue
        break
    tge.console.clear()
    game: Game = deepcopy(GAMES["games"][game_id]["game"])
    frame = game.setup(user)
    while True:
        tge.console.clear()
        print(frame)
        user_input = input()
        if len(user_input) != 1 or not user_input:
            continue
        user_input = redirect_key(user_input)
        if user_input in GAMES["games"][game_id]["inputs"]:
            input_id = GAMES["games"][game_id]["inputs"].index(user_input)
        else:
            continue
        next_frame = game.main(input_id, user)
        if next_frame is None:
            print("\nAn error has occurred.")
            input()
            break
        if next_frame:
            if isinstance(next_frame, str):
                frame = next_frame
            if isinstance(next_frame, list):
                frame = next_frame[0]
                tge.console.clear()
                print(frame)
                input()
                break
