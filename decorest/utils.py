import inspect
import six


def dict_from_args(func, *args):
    """
    Convert function arguments to a dictionary
    """
    result = {}
    args_names = []

    if six.PY2:
        args_names = inspect.getargspec(func)[0]
    else:
        args_names = list(inspect.signature(func).parameters.keys())

    for i in range(len(args)):
        result[args_names[i]] = args[i]

    return result


def merge_dicts(*dict_args):
    """
    Merges all dicts passed as arguments, skips None objects.
    Repeating keys will replace the keys from previous dicts.
    """
    result = {}
    for dictionary in dict_args:
        if dictionary is not None:
            result.update(dictionary)
    return result
