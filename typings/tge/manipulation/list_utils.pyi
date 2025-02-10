from _typeshed import Incomplete
from collections.abc import Iterable
from typing import Any
__all__=['list_mul','remove_duplicates','count_occurrences','calculate_average','find_common_elements','median','reverse_list','find_max_min_difference','find_missing_number','greatest_product','zipper_insert','compress_list','compress_list_of_lists','decompress_list','decompress_list_of_lists','MaxSizeList','split_with_list']
def list_mul(lst:list[int|float])->int|float:...
def remove_duplicates(list:list[Any])->list[Any]:...
def count_occurrences(list:list[Any],item:Any)->int:...
def calculate_average(lst:list[int|float])->float:...
def find_common_elements(lst1:list[Any],lst2:list[Any])->list[Any]:...
def median(lst:list[int|float])->float:...
def reverse_list(lst:list[Any])->list[Any]:...
def find_max_min_difference(lst:list[int])->int:...
def find_missing_number(lst:list[int])->int:...
def greatest_product(lst:list[int],lst2:list[int])->int:...
def zipper_insert(list1:list[Any],list2:list[Any])->list[Any]:...
def compress_list(list_to_compress:list[Any])->Any|list[Any]:...
def compress_list_of_lists(list_to_compress:list[list[Any]])->list[list[Any]]:...
def decompress_list(list_to_decompress:list[int|str|None]|Any,width:int)->list[Any]:...
def decompress_list_of_lists(list_to_decompress:list[list[int|Any]|Any],width:int)->list[list[Any]]:...
class MaxSizeList(list[Any]):
	max_size:Incomplete
	def __init__(self,max_size:int)->None:...
	def append(self,item:Any):...
	def extend(self,iterable:Iterable[Any]):...
def split_with_list(string:str,separators:list[str],limit:None|int=None)->list[str]:...