import engine
import tge
from wrapper.console_bios import wait_for_key, send

user = tge.tbe.get_username()
e = engine.Engine()

new = ""

while True:
    while True:
        tge.console.clear()
        out = e.select_game_from_user(user, new)
        if isinstance(out, engine.SelectedGame):
            break
        print(out)
        new = wait_for_key()


    print("Selected: %s" % out)

    while True:
        new = wait_for_key()
        if new == "&":
            quit()
        game_output = e.run_game(new, user.lower(), user)
        if isinstance(game_output, engine.ChangeInputs):
            game_output = game_output.frame
        if game_output is None:
            continue
        if isinstance(game_output, engine.StopEngine):
            tge.console.clear()
            print(game_output.last_frame + "\nEnd.")
            break
        if isinstance(game_output, str):

            send(game_output)
        else:
            tge.console.clear()
            print("Error:\n%s" % "\n".join(game_output.args))
        print()
