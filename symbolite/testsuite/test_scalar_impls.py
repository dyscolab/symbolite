import math as pymath
import types
from operator import attrgetter
from typing import Any

import pytest

from symbolite.core import Unsupported
from symbolite.impl import get_all_implementations

all_impl = get_all_implementations()

# Available functions and their test values
_functions = {
    "abs": (3,),
    "acos": (0.5,),
    "acosh": (3,),
    "asin": (0.5,),
    "asinh": (3,),
    "atan": (3,),
    "atan2": (1, 2),
    "atanh": (0.5,),
    "ceil": (3,),
    "comb": (3, 2),
    "copysign": (1, 2),
    "cos": (3,),
    "cosh": (3,),
    "degrees": (3,),
    "erf": (3,),
    "erfc": (3,),
    "exp": (3,),
    "expm1": (3,),
    "fabs": (3,),
    "factorial": (3,),
    "floor": (3,),
    "fmod": (1, 2),
    "frexp": (3.0,),
    "gamma": (3,),
    # "gcd": (1, 2),
    # "hypot": (1, 2),
    # "isclose": (1, 2),
    "isfinite": (3,),
    "isinf": (3,),
    "isnan": (3,),
    "isqrt": (3,),
    # "lcm": (3, 2),
    "ldexp": (1, 2),
    "lgamma": (3,),
    "log": (3,),
    "log10": (3,),
    "log1p": (3,),
    "log2": (3,),
    "modf": (3.0,),
    "nextafter": (3, 4),
    # "perm": (3,),
    "pow": (1, 2),
    "radians": (3,),
    "remainder": (1, 2),
    "sin": (3,),
    "sinh": (3,),
    "sqrt": (3,),
    "tan": (3,),
    "tanh": (3,),
    "trunc": (3,),
    "ulp": (3,),
}

_values = {
    "e": None,
    "inf": None,
    "pi": None,
    "nan": None,
    "tau": None,
}

_all = {**_functions, **_values}


def almost_equal(x: Any, y: Any, threshold: float = 0.0001):
    if isinstance(x, bool):
        assert x == y
    elif isinstance(x, tuple):
        for el0, el1 in zip(x, y):
            almost_equal(el0, el1, threshold)
    else:
        if pymath.isnan(x):
            assert pymath.isnan(y)
        elif pymath.isinf(x):
            assert pymath.isinf(y)
        else:
            assert abs(x - y) < threshold, (x, "!=", y)


@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_is_defined(libsl: types.ModuleType):
    """Test that that all included libraries define members defined in symbolite.lib"""
    for k in tuple(_functions.keys()) + tuple(_values.keys()):
        name = f"scalar.{k}"
        try:
            attrgetter(name)(libsl)
        except AttributeError:
            assert False, f"{name} not defined."


@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
@pytest.mark.parametrize("func_name_and_values", _all.items(), ids=_all.keys())
def test_compare(libsl: types.ModuleType, func_name_and_values: tuple[Any, Any]):
    """Compare implementation for different mappers
    for a (very small) subset of values.
    """
    func_name, test_values = func_name_and_values

    try:
        original_func = getattr(pymath, func_name)
    except AttributeError:
        # This is a function not on math, but rather on builtins
        try:
            original_func = __builtins__[func_name]
        except KeyError:
            # This is a function not on math and not on builtins
            # It is a function added in later Python versions.
            return

    mapped_func = attrgetter("scalar." + func_name)(libsl)

    if mapped_func is Unsupported:
        return

    if test_values is None:
        almost_equal(original_func, mapped_func)
    elif isinstance(test_values, tuple):
        almost_equal(original_func(*test_values), mapped_func(*test_values))
    elif isinstance(test_values, list):
        almost_equal(original_func(test_values), mapped_func(test_values))
    else:
        assert False, "Unknown test values"
