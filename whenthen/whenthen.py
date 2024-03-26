
def whenthen(func):
    conditions = {}

    def wrapper(*agrs, **kwargs):
        for condition in conditions:
            if condition(*agrs, **kwargs):
                return conditions[condition](*agrs, **kwargs)
        return func(*agrs, **kwargs)


    def when(func_when):
        if conditions:
            last_value_condition = list(conditions.keys()).pop()
            if conditions[last_value_condition] is None:
                raise ValueError
        conditions[func_when] = None
        return wrapper


    def then(func_then):
        last_value_condition = list(conditions.keys()).pop()
        if conditions[last_value_condition] is not None:
            raise ValueError
        conditions[last_value_condition] = func_then
        return wrapper

    wrapper.when = when
    wrapper.then = then
    return wrapper


@whenthen
def fract(x):
    return x * fract(x - 1)


@fract.when
def fract(x):
    return x == 0


@fract.then
def fract(x):
    return 1


@fract.when
def fract(x):
    return x > 10


@fract.then
def fract(x):
    return x * (x - 1) * (x - 2) * (x - 3) * (x - 4) * fract(x - 5)
