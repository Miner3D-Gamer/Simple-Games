import ctypes
from .. import SYSTEM_NAME as SYSTEM_NAME

USER32: ctypes.WinDLL
KERNEL32: ctypes.WinDLL
CF_UNICODETEXT: int
GMEM_DDESHARE: int
GMEM_MOVEABLE: int
GHND = GMEM_DDESHARE | GMEM_MOVEABLE
win_dll_type = ctypes.WinDLL
