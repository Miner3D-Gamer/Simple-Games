from.middle_man import*
from PIL import Image
__all__=['count_gif_frames','image_to_ascii','count_image_colors','hex_to_rgb','Color','is_color_similar']
def count_gif_frames(gif:Image.Image)->int:...
def image_to_ascii(image_path:str='',image:Image.Image|None=None,width:int|None=None,unicode:bool=False,ascii_chars:str='')->str:...
def count_image_colors(image:Image.Image|None=None,image_path:str|None=None)->list[tuple[int,int,int]]:...
def hex_to_rgb(hex_color:str)->tuple[int,int,int]:...
class Color:
	color:list[int]
	def __init__(self,color:tuple[int,int,int])->None:...
	def __iter__(self):...
	def get(self)->list[int]:...
	def __call__(self):...
def is_color_similar(a:tuple[int|float,int|float,int|float],b:tuple[int|float,int|float,int|float],similarity:int|float)->bool:...