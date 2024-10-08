from inspect import signature
from typing import Any, Callable


def setup_func(func: Callable[..., Any], **kwargs: Any) -> Any:
    """
    Setup a Coroutine function with the required arguments from the kwargs
    :param func: The function to setup
    :param kwargs: The arguments that may be passed to the function if the function requires them
    :return: The result of the function
    """
    parameters = signature(func).parameters
    func_kwargs = {}
    for name, parameter in parameters.items():
        if name in kwargs:
            func_kwargs[name] = kwargs[name]
        elif parameter.default != parameter.empty:
            func_kwargs[name] = parameter.default
        else:
            raise TypeError(f"Missing required argument {name}")
    return func(**func_kwargs)
