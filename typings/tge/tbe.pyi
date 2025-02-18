from.manipulation.list_utils import split_with_list as split_with_list
from typing import Any,Callable,Iterator
__all__=['pass_func','execute_function','determine_affirmative','get_available_variables','number_to_words','letter_to_number','number_to_letter','find_undocumented_functions','check_directory_for_undocumented_functions','check_directory_and_sub_directory_for_undocumented_functions','autocomplete','strict_autocomplete','is_iterable','split_with_list','analyze_text','divide','DualInfinite','generate_every_capitalization_states','remove_unused_libraries','repeat','get_username','profile','profile_function','get_current_pip_path','ArgumentHandler','HashMap','print_undocumented_functions_in_directory','minify','compress_imports_in_code']
def pass_func(*args:Any,**more_args:Any)->None:...
def execute_function(func:Callable[...,Any]=...,*args:Any,**kwargs:Any)->Any:...
def determine_affirmative(text:str)->bool|None:...
def get_available_variables()->dict[str,Any]:...
def number_to_words(number:int)->str:...
def letter_to_number(letter:str)->int:...
def number_to_letter(number:int)->str:...
def find_undocumented_functions(file_path:str)->list[list[str|int|None]]:...
def check_directory_for_undocumented_functions(directory_path:str)->dict[str,list[list[str|int|None]]]:...
def check_directory_and_sub_directory_for_undocumented_functions(directory_path:str)->dict[str,list[list[str|int|None]]]:...
def autocomplete(prefix:str,word_list:list[str])->list[str]:...
def strict_autocomplete(prefix:str,word_list:list[str])->list[str]|str:...
def is_iterable(thing:Any)->bool:...
def analyze_text(text:str)->dict[str,str|list[int]|float]:...
class DualInfinite:...
def divide(a:int|float,b:int|float)->float|DualInfinite:...
def generate_every_capitalization_states(s:str)->list[str]:...
def remove_unused_libraries(code_str:str)->str:...
def repeat(times:int,func:Callable[...,Any],*args:Any,**kwargs:Any)->Any:...
def get_username()->str:...
def profile(func:Callable[...,Any])->Callable[...,Any]:...
def profile_function(function,filename:str,*inputs,**extra):...
def get_current_pip_path()->str|None:...
class ArgumentHandler:
	arguments:list[str];argument_list_length:int
	def __init__(self,arguments:None|list[str]=None)->None:...
	def has_argument(self,argument:str,delete:bool=False)->bool:...
	def get_argument_by_flag(self,flag:str,delete:bool=False,default:Any=None)->str|None:...
	def get_id(self,item:str)->int:...
	def is_empty(self)->bool:...
class HashMap:
	map:list[Any]
	def __init__(self,*items:Any)->None:...
	def append(self,value:Any)->None:...
	def extend(self,values:list[Any])->None:...
	def pop(self,index:int)->Any:...
	def remove(self,value:Any)->None:...
	def index(self,value:Any)->int:...
	def __getitem__(self,index:int)->Any:...
	def clear(self)->None:...
	def __iter__(self)->Iterator[Any]:...
	def __contains__(self,item:Any)->bool:...
def print_undocumented_functions_in_directory(directory:str=...)->int:...
def minify(text:str,*,rename_globals:bool=False,remove_docstrings:bool=True,remove_annotations:bool=True,rename_locals:bool=False)->str:...
def compress_imports_in_code(code:list[str])->list[str]:...