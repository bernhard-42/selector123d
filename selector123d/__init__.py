from .selector import *
from .states import *


def flatten(l):
    result = []
    for el in l:
        if isinstance(el, list):
            result.extend(el)
        else:
            result.append(el)
    return result
