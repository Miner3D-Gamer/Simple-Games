from..import SYSTEM_NAME as SYSTEM_NAME
import ctypes
USER32:ctypes.WinDLL
KERNEL32:ctypes.WinDLL
CF_UNICODETEXT:int
GMEM_DDESHARE:int
GMEM_MOVEABLE:int
GHND:int
win_dll_type=ctypes.WinDLL