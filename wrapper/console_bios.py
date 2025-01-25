import platform
from custom_typing import *


def send(msg: str) -> dict[LOGGING_ANNOTATION, str]:
    # ANSI escape sequence to move cursor to top-left corner
    CURSOR_UP = "\033[H"
    # ANSI escape sequence to clear from cursor to end of screen
    CLEAR_FROM_CURSOR = "\033[J"

    print(f"{CURSOR_UP}{CLEAR_FROM_CURSOR}{msg}", end="", flush=True)

    return {}

def wait_for_key_windows() -> str:
    key = msvcrt.getch()
    # Handle ctrl-c
    if key == b"\x03":
        raise KeyboardInterrupt()

    # Handle backspace
    if key == b"\x08":
        return "BACKSPACE"
    
    # Handle enter
    if key == b"\x0d":
        return "ENTER"

    # Handle tab
    if key == b"\x09":
        return "TAB"

    # Handle extended keys
    if key in {b"\x00", b"\xe0"}:
        ext_key = msvcrt.getch()
        key_map = {
            b"H": "UP",
            b"P": "DOWN",
            b"K": "LEFT",
            b"M": "RIGHT",
            b"O": "END",
            b"Q": "PAGE_DOWN",
            b"I": "PAGE_UP",
            b"G": "HOME",
            b"S": "DELETE",
            b"R": "INSERT",
            b";": "F1",
            b"<": "F2",
            b"=": "F3",
            b">": "F4",
            b"?": "F5",
            b"@": "F6",
            b"A": "F7",
            b"B": "F8",
            b"C": "F9",
            b"D": "F10",
            b"E": "F11",
            b"F": "F12",
            b"s": "BIG_LEFT",
            b"t": "BIG_RIGHT",
        }
        return key_map.get(ext_key, f"EXT_{hex_to_ascii(ext_key.hex())}")

    # Decode other keys
    return key.decode(locale.getpreferredencoding(), errors="replace")


def wait_for_key_unix()-> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x1b":  # Escape sequence (potential extended key)
            key += sys.stdin.read(1)
            if key[1] == "[":
                while True:
                    next_char = sys.stdin.read(1)
                    key += next_char
                    if next_char.isalpha() or next_char == "~":
                        break
            EXT_KEY_MAP = {
                "[A": "UP",
                "[B": "DOWN",
                "[D": "LEFT",
                "[C": "RIGHT",
                "[F": "END",
                "[6~": "PAGE_DOWN",
                "[5~": "PAGE_UP",
                "[H": "HOME",
                "[3~": "DELETE",
                "[2~": "INSERT",
                "OP": "F1",
                "OQ": "F2",
                "OR": "F3",
                "OS": "F4",
                "[15~": "F5",
                "[17~": "F6",
                "[18~": "F7",
                "[19~": "F8",
                "[20~": "F9",
                "[21~": "F10",
                "[23~": "F11",
                "[24~": "F12",
                "[1;2D": "BIG_LEFT",
                "[1;2C": "BIG_RIGHT",
                "\x08": "BACKSPACE",
                "\x7f": "BACKSPACE",
            }
            return EXT_KEY_MAP.get(key, f"EXT_{key}")
        elif key == "\x03":  # Ctrl-C
            raise KeyboardInterrupt()
        return key.decode(locale.getpreferredencoding(), errors="replace")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


system = platform.system()
if system == "Windows":
    import msvcrt
    import locale

    wait_for_key = wait_for_key_windows
elif system in ["Linux", "Darwin"]:
    import termios
    import tty
    import sys

    wait_for_key = wait_for_key_unix
else:
    raise NotImplementedError(f"Platform '{system}' is not supported.")


def hex_to_ascii(hex_string):
    return "".join(
        [chr(int(hex_string[i : i + 2], 16)) for i in range(0, len(hex_string), 2)]
    )
