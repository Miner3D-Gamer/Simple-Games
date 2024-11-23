from types import MethodType, ModuleType
from typing import Any, Callable, NoReturn

__all__ = ['run_function_with_timeout', 'get_docstring', 'check_for_functions_in_module_with_missing_notations', 'print_check_for_functions_in_module_with_missing_notations', 'get_function_inputs', 'get_return_type', 'count_functions_in_library']

def get_docstring(obj: object) -> str | None: ...
def check_for_functions_in_module_with_missing_notations(library_module: ModuleType) -> NoReturn: ...
def print_check_for_functions_in_module_with_missing_notations(library_module: ModuleType) -> None: ...
def get_return_type(func: MethodType) -> Any: ...
def get_function_inputs(func: MethodType) -> list[dict[str, Any]]: ...

class UnknownInputType: ...

def count_functions_in_library(library_name: str) -> int: ...

class NoInputType: ...
class MissingReturnType: ...
class TimeoutResult: ...

def run_function_with_timeout(func: Callable[..., Any], timeout: int | float, *args: Any, **kwargs: Any) -> Any | TimeoutResult: ...
