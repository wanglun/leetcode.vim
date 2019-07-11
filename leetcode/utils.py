from enum import Enum
from typing import Any, Union

PRIMITIVE_TYPES = (int, float, bool, str)

LIST_TYPES = (list, tuple)

DICT_TYPES = (dict,)

PlainType = Union[int, float, None, bool, str, list, dict]


def to_plain(obj: Any) -> PlainType:
    if obj is None:
        return obj

    if isinstance(obj, PRIMITIVE_TYPES):
        return obj

    if isinstance(obj, LIST_TYPES):
        return [to_plain(element) for element in obj]

    if isinstance(obj, DICT_TYPES):
        return {to_plain(key): to_plain(value)
                for key, value in obj.items()}

    if isinstance(obj, Enum):
        return obj.value

    result = {}
    for key, value in obj.__dict__.items():
        result[to_plain(key)] = to_plain(value)

    return result


def wrap_call(api, *args, **kwargs):
    try:
        result = api(*args, **kwargs)
        return {
            'status': 'ok',
            'body': to_plain(result),
        }
    except Exception as exn:  # pylint: disable=W0703
        return {
            'status': 'error',
            'body': str(exn),
        }
