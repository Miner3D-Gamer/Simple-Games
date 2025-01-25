from custom_typing import ALL_FINE, LOGGING_ANNOTATION, INFO, WARNING, DEBUG, ERROR, FATAL_ERROR
from wrapper.shared import get_time_stamp

from typing import Any
def console_log(*msg: Any):
    print(*msg)





def log(msg: str, logging: LOGGING_ANNOTATION = ALL_FINE) -> bool:
    if logging is ALL_FINE:
        console_log("[%s] > %s" % (get_time_stamp(), msg))
        return False
    if logging is INFO:
        console_log("[%s] INFO> %s" % (get_time_stamp(), msg))
        return False
    if logging is WARNING:
        console_log("[%s] WARNING> %s" % (get_time_stamp(), msg))
        return False
    if logging is DEBUG:
        console_log("[%s] DEBUG> %s" % (get_time_stamp(), msg))
        return False
    if logging is ERROR:
        console_log("[%s] ERROR> %s" % (get_time_stamp(), msg))
        return False
    if logging is FATAL_ERROR:
        console_log("[%s] FATAL_ERROR> %s" % (get_time_stamp(), msg))
        return True

    log("Unknown logging type: %s for '%s'" % (logging, msg), ERROR)
    return False