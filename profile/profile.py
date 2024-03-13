import time
import types
from functools import wraps


def profile(obj: types.FunctionType | type) -> types.FunctionType | type:
    def wrapper(func: types.FunctionType) -> types.FunctionType:
        @wraps(func)
        def decorator_func(*args, **kwargs):
            func_name = str(func).split()[1]
            print(f'{func_name} started')
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f'{func_name} finished in {end_time - start_time}s')
            return result
        return decorator_func

    if isinstance(obj, types.FunctionType):
        return wrapper(obj)
    elif isinstance(obj, type):
        for attr in obj.__dict__:
            if callable(getattr(obj, attr)):
                setattr(obj, attr, wrapper(obj.__dict__[attr]))
        return obj


###TESTS###
@profile
def func(x: int, y: int) -> int:
    for i in range(x):
        x += i ** y
    return x

func(15, 10)
func(70, 4)


@profile
class Class:
    def __init__(self, value):
        self.value = value

    def a(self) -> int:
        for i in range(self.value):
            pass
        time.sleep(2)
        return i

    def b(self) -> str:
        result = ''
        for i in range(self.value):
            if i % 2:
                result += str(i)
        return result

Class(100)
C = Class(50000)
C.a()
C.b()
