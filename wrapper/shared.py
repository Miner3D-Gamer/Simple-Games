import time
from typing import Any

def pad_value(val: Any, how_many: int, char: str) -> str:
    return str(val).rjust(how_many, char)

def get_time_stamp() -> str:
    now = time.localtime()
    return (
        f"{now.tm_year}"
        + "-"
        + pad_value(now.tm_mon, 2, "0")
        + "-"
        + pad_value(now.tm_mday, 2, "0")
        + "-"
        + pad_value(now.tm_hour, 2, "0")
        + ":"
        + pad_value(now.tm_min, 2, "0")
        + ":"
        + pad_value(now.tm_sec, 2, "0")
    )
