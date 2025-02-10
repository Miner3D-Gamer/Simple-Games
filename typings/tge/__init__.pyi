from.import audio as audio,bool_operations as bool_operations,console_utils as console,file_operations as file_operations,formatting_utils as formatting,function_utils as function_utils,internet as internet,library_utils as library_utils,random_generators as random,tbe as tbe,time_utils as time_utils
from.codec import codec as codec
from.compatibility import tge_pygame as tge_pygame,tge_tkinter as tge_tkinter
from.conversion import binary as binary_conversion,data as data_conversion,temperature as temperature_conversion,time as time_conversion,units as units_conversion
from.image_processing import image_operations as image_operations
from.manipulation import dictionary_utils as dict_utils,expansions as expansions,list_utils as list_utils,string_utils as string_utils
from.math_functions import financial_calculations as financial_calculations,geometry_calculations as geometry_calculations,math_functions as math_functions,statistics_calculations as statistics_calculations
from.system_interactions import clipboard_operations as clipboard,cursor_operations as cursor,keyboard_operations as keyboard,window_manager as window_manager
from.validation import validation as validation
from _typeshed import Incomplete
from typing import Any,Callable,Literal
__all__=['library_utils','is_ffmpeg_installed','get_system','is_tge_outdated','__name__','__author__','__license__','__url__','__doc__','SYSTEM_NAME','INIT_TIME','INIT_TIME_BEFORE_IMPORTING','burn_value_into_function','string_utils','list_utils','dict_utils','expansions','binary_conversion','temperature_conversion','time_conversion','units_conversion','data_conversion','financial_calculations','geometry_calculations','math_functions','statistics_calculations','clipboard','cursor','keyboard','window_manager','validation','codec','console','random','internet','tbe','time_utils','file_operations','formatting','bool_operations','image_operations','function_utils','audio','string_utils','list_utils','dict_utils','expansions','binary_conversion','temperature_conversion','time_conversion','units_conversion','data_conversion','tge_tkinter','financial_calculations','geometry_calculations','function_utils','time_utils','formatting','bool_operations','validation','tge_pygame','math_functions','statistics_calculations','clipboard','cursor','keyboard','window_manager','codec','random','file_operations','tbe','console','internet','image_processing','audio']
__name__:str
__author__:str
__license__:str
__url__:str
__doc__:str
def is_tge_outdated()->bool:...
def burn_value_into_function(x:Any)->Callable[[],Any]:...
def get_system()->Literal['jython','darwin','windows','linux','unknown']:...
SYSTEM_NAME:Incomplete
def is_ffmpeg_installed():...
INIT_TIME_BEFORE_IMPORTING:Incomplete
INIT_TIME:Incomplete