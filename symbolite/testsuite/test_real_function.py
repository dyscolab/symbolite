import inspect
import types
from typing import Any

import pytest

from symbolite import Symbol, real
from symbolite.core.variable import Variable
from symbolite.impl import get_all_implementations
from symbolite.ops import as_function, substitute
from symbolite.ops.base import symbol_names, translate

all_impl = get_all_implementations()

x, y, z = map(real.Real, "x y z".split())

xsy = real.Real("xsy")


@pytest.mark.mypy_testing
def test_typing():
    reveal_type(x + y)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(2 + y)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(x + 2)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(x + xsy)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(xsy + x)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(real.cos(x))  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(real.cos(xsy))  # R: symbolite.abstract.real.Real # noqa: F821


@pytest.mark.parametrize(
    "expr",
    [
        x + y,
        x - y,
        x * y,
        x / y,
        x**y,
        x // y,
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_known_symbols(expr: Variable, libsl: types.ModuleType):
    f = as_function(expr, libsl=libsl)
    assert f.__name__ == "f"
    assert translate(substitute(expr, {x: 2, y: 3}), libsl=libsl) == f(2, 3)
    assert tuple(inspect.signature(f).parameters.keys()) == ("x", "y")


# x = 2, y = 3, z = 1
f1 = 2 * x + y
f2 = (f1, 3 * x, 4 * z)
f3 = {"a": f1, "b": 3 * x, "c": 4 * z}


@pytest.mark.parametrize(
    "expr,params,args,result",
    [
        (f1, ("x", "y"), (2, 3), 7),
        (f2, ("x", "y", "z"), (2, 3, 1), (7, 6, 4)),
        (f3, ("x", "y", "z"), (2, 3, 1), {"a": 7, "b": 6, "c": 4}),
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_as_function(expr, params, args, result, libsl: types.ModuleType):
    f = as_function(expr, libsl=libsl)
    assert f.__name__ == "f"
    assert tuple(inspect.signature(f).parameters.keys()) == params
    assert f(*args) == result


@pytest.mark.parametrize(
    "expr,replaced",
    [
        (x + real.cos(y), 2 + real.cos(3)),
        (x + real.pi * y, 2 + real.pi * 3),
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_lib_symbols(expr: Variable[Any], replaced: Symbol, libsl: types.ModuleType):
    f = as_function(expr, libsl=libsl)
    value = f(2, 3)
    assert f.__name__ == "f"
    assert translate(substitute(expr, {x: 2, y: 3}), libsl=libsl) == value
    assert tuple(inspect.signature(f).parameters.keys()) == ("x", "y")


@pytest.mark.parametrize(
    "expr,namespace,result",
    [
        (
            x + real.pi * real.cos(y),
            None,
            {
                "x",
                "y",
                "real.cos",
                "real.pi",
                "real.mul",
                "real.add",
            },
        ),
        (x + real.pi * real.cos(y), "", {"x", "y"}),
        (
            x + real.pi * real.cos(y),
            "real",
            {"real.cos", "real.pi", "real.mul", "real.add"},
        ),
    ],
)
def test_list_symbols(expr: Variable[Any], namespace: str | None, result: Symbol):
    assert symbol_names(expr, namespace) == result
