class Game:
    def __init__(self) -> None: ...
    def main(self, input: int, user: str) -> None | dict: ...
    def setup(self, user: str) -> tuple[str, str]: ...
    def info(self) -> dict: ...


import os
import tge
import importlib
from copy import deepcopy
import traceback
import sys

GAMES = {"games": {}}


def load_inputs(inputs: str | list) -> tuple[list, str]:
    if isinstance(inputs, str):
        match inputs:
            case "arrows":

                inputs = [*"⬅⬆⬇➡"]
    elif not tge.tbe.is_iterable(inputs):
        return [], "Inputs are not iterable"

    if isinstance(inputs, str):
        return [], "Invalid input preset"
    return inputs, ""


def load_game(game: Game):
    try:
        game = game()
    except Exception as e:
        return "Error occurred while trying to load game: %s %s" % (e, traceback.format_exc())

    if not hasattr(game, "info"):
        return "Error: Missing game info -> info()"
    if not hasattr(game, "main"):
        return "Error: Missing game mainloop -> main()"
    if not hasattr(game, "setup"):
        return "Error: Missing game setup -> setup()"
    try:
        info = game.info()
    except Exception as e:
        return "Error occurred while trying to receive info from game: %s" % e
    if not isinstance(info, dict):
        return "Invalid info typing: %s" % type(info)
    name = info.get("name", "")
    id = info.get("id", "")
    inputs = info.get("inputs", "")

    if isinstance(inputs, str):
        if inputs:
            inputs, errors = load_inputs(inputs)
            if errors:
                return errors
    else:
        return "Invalid type of initial inputs received"

    if isinstance(id, str):
        if not id:
            return "Id cannot be empty"
    else:
        return "Invalid id type"

    if isinstance(name, str):
        if not name:
            return "Name cannot be empty"
    else:
        return "Invalid name type"

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
                print("Error importing %s:\n%s" % (dir, error), traceback.print_exc())
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
    try:
        frame, requested_inputs = game.setup(user)
    except Exception as e:
        input("Error while receiving initial from from game: %s" % e)
        continue
    accepted_inputs, errors = load_inputs(requested_inputs)
    if errors:
        input("Received invalid input request while trying to load game: %s" % errors)
        continue
    while True:
        tge.console.clear()
        print(frame)
        user_input = input()
        if user_input.startswith("& "):
            quit()

        if len(user_input) != 1 or not user_input:
            continue
        if user_input in accepted_inputs:
            input_id = accepted_inputs.index(user_input)
        else:
            user_input = redirect_key(user_input)
            if user_input in accepted_inputs:
                input_id = accepted_inputs.index(user_input)
            else:
                continue
        try:
            output = game.main(input_id, user)
        except SystemExit:
            break
        except KeyboardInterrupt:
            input("\nForce closed the game")
            break
        except BaseException as e:
            print("\nAn error has occurred; %s" % e)
            traceback.print_exc()
            input("\nPress Enter to continue...")
            break

        if output is None:
            input("\nAn error has occurred. More is not known")
            break

        if output:
            if not isinstance(output, dict):
                input("\nInvalid return type: %s" % type(output))
                break
            action = output.get("action", "")
            new_frame = output.get("frame", "")
            if isinstance(new_frame, str) and new_frame != "":
                frame = new_frame
            if isinstance(action, str) and action != "":
                if action == "end":
                    tge.console.clear()
                    input(frame)
                    break
                if action == "change_inputs":
                    requested_inputs = output.get("inputs", "")
                    if requested_inputs != "":
                        accepted_inputs, errors = load_inputs(accepted_inputs)
                        if errors:
                            input(
                                "\nReceived invalid input request when application tried changing inputs: %s"
                                % errors
                            )
                            break
