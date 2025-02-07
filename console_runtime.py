import framework
import tge
import os
from wrapper.console_bios import wait_for_key, send
from typing import Optional, Union


def to_console(
    game_output: Optional[
        Union[
            BaseException,
            str,
            framework.StopFramework,
            framework.ChangeInputs,
            framework.SelectedGame,
        ]
    ]
) -> bool:
    """
    Returns: bool - True if the framework should stop, False to continue
    """
    global old_frame
    # Normal Frame
    if isinstance(game_output, str):
        tge.console.clear()
        old_frame = game_output
        send(game_output + "\n")
        return False

    # Change inputs
    if isinstance(game_output, framework.ChangeInputs):
        # Since the framework filters out all invalid keys, we don't need to do anything
        game_output = game_output.frame
        if game_output is None:
            return False
        else:
            return to_console(game_output)

    # Stop
    if isinstance(game_output, framework.StopFramework):
        # Game or Framework requested to stop
        tge.console.clear()
        old_frame = game_output.last_frame + "\nEnd."
        send(old_frame)
        quit()

    # Selected Game from list
    if isinstance(game_output, framework.SelectedGame):
        # old_frame = "Selected: %s (%s)" % (game_output.name, game_output.id)
        # send(old_frame)
        # wait_for_key()
        return True

    # Error
    if isinstance(game_output, BaseException):
        tge.console.clear()
        old_frame = "Error:\n%s" % "\n".join(game_output.args)
        send(old_frame + "\n")
        return False

    # This means the frame hasn't changed and as such doesn't need to be printed
    if game_output is None:
        return False

    # Wonky
    raise BaseException(
        "Unexpected output: '%s' (%s)"
        % (game_output.replace("\n", "\\n"), type(game_output))
    )


def commands():
    command = ""

    while True:
        tge.console.clear()
        send(command)
        inp = wait_for_key()

        if inp == "BACKSPACE":
            command = command[:-1]
        elif inp == "ENTER":
            break
        else:
            command += inp

    args = command.split()
    if not args:
        send("No command entered. Try again.\n")
        wait_for_key()
        to_console(old_frame)
        return

    cmd, *params = args

    commands_map = {
        "user": lambda p: set_user(p) if p else send("Please provide a username.\n"),
        "game": lambda p: (
            framework_instance.select_game(p[0], user)
            if p
            else send("Please provide a game ID.\n")
        ),
        "quit": lambda p: quit(),
    }

    if cmd in commands_map:
        commands_map[cmd](params)
    else:
        send(
            "Unknown command, try one of these instead: %s.\n"
            % (", ".join(commands_map.keys()))
        )
        wait_for_key()
    to_console(old_frame)


def set_user(params):
    global user
    user = params[0]


def get_console_size():
    return os.get_terminal_size().columns, 0


fast_quit = lambda x: "" if x != "&" else quit()

user = tge.tbe.get_username()
framework_instance = framework.Framework("console")

old_frame = ""

while True:
    new = ""
    while True:
        out = framework_instance.select_game_from_user(user, new)
        if to_console(out):
            break
        new = wait_for_key()
        fast_quit(new)
        if new == "@":
            commands()
            new = ""

    while True:
        new = wait_for_key()
        fast_quit(new)
        if new == "@":
            commands()
            new = ""
            continue
        framework_instance.set_container_size(get_console_size())
        game_output = framework_instance.run_game(
            new,
            {
                "username": user,
                "user_id": user.lower().replace(" ", "_"),
                "debug_mode": False,
            },
        )
        if to_console(game_output):
            break
