"""
This type stub file was generated by pyright.
"""

"""
This type stub file was generated by pyright.
"""
_benchmarks = ...
def benchmark(f):
    ...

@benchmark
def long_list(n):
    ...

@benchmark
def big_int_object(n):
    ...

@benchmark
def big_decimal_object(n):
    ...

@benchmark
def big_null_object(n):
    ...

@benchmark
def big_bool_object(n):
    ...

@benchmark
def big_str_object(n):
    ...

@benchmark
def big_longstr_object(n):
    ...

@benchmark
def object_with_10_keys(n):
    ...

@benchmark
def empty_lists(n):
    ...

@benchmark
def empty_objects(n):
    ...

def parse_benchmarks(s):
    ...

BACKEND_NAMES = ...
def load_backends():
    ...

_backends = ...
def parse_backends(s):
    ...

class progress_message:
    def __init__(self, message) -> None:
        ...
    
    def __enter__(self):
        ...
    
    def __exit__(self, *args):
        ...
    


class AsyncReader:
    def __init__(self, data) -> None:
        ...
    
    async def read(self, n=...):
        ...
    
    def close(self):
        ...
    


def median(values):
    ...

def stats(values):
    ...

def run_benchmarks(args, benchmark_func=..., fname=...):
    ...

def main():
    ...

if __name__ == '__main__':
    ...