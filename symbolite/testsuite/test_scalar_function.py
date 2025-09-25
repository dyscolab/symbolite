import inspect
import types

import pytest

from symbolite import Symbol, scalar
from symbolite.impl import get_all_implementations
from symbolite.ops import as_function, substitute
from symbolite.ops.base import symbol_names, evaluate

all_impl = get_all_implementations()

x, y, z = map(scalar.Scalar, "x y z".split())

xsy = Symbol("xsy")


@pytest.mark.mypy_testing
def test_typing():
    reveal_type(x + y)  # R: symbolite.abstract.scalar.Scalar # noqa: F821
    reveal_type(2 + y)  # R: symbolite.abstract.scalar.Scalar # noqa: F821
    reveal_type(x + 2)  # R: symbolite.abstract.scalar.Scalar # noqa: F821
    # reveal_type(x + xsy) # R: symbolite.abstract.symbol.Symbol # noqa: F821
    # reveal_type(xsy + x) # R: symbolite.abstract.symbol.Symbol # noqa: F821
    reveal_type(scalar.cos(x))  # R: symbolite.abstract.scalar.Scalar # noqa: F821
    # reveal_type(scalar.cos(xsy)) # R: symbolite.abstract.scalar.Scalar # noqa: F821


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
def test_known_symbols(expr: Symbol, libsl: types.ModuleType):
    f = as_function(expr, libsl=libsl)
    assert f.__name__ == "f"
    assert evaluate(substitute(expr, {x: 2, y: 3}), libsl=libsl) == f(2, 3)
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
        (x + scalar.cos(y), 2 + scalar.cos(3)),
        (x + scalar.pi * y, 2 + scalar.pi * 3),
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_lib_symbols(expr: Symbol, replaced: Symbol, libsl: types.ModuleType):
    f = as_function(expr, libsl=libsl)
    value = f(2, 3)
    assert f.__name__ == "f"
    assert evaluate(substitute(expr, {x: 2, y: 3}), libsl=libsl) == value
    assert tuple(inspect.signature(f).parameters.keys()) == ("x", "y")


@pytest.mark.parametrize(
    "expr,namespace,result",
    [
        (
            x + scalar.pi * scalar.cos(y),
            None,
            {
                "x",
                "y",
                "scalar.cos",
                "scalar.pi",
                "symbol.mul",
                "symbol.add",
            },
        ),
        (x + scalar.pi * scalar.cos(y), "", {"x", "y"}),
        (
            x + scalar.pi * scalar.cos(y),
            "scalar",
            {"scalar.cos", "scalar.pi"},
        ),
    ],
)
def test_list_symbols(expr: Symbol, namespace: str | None, result: Symbol):
    assert symbol_names(expr, namespace) == result
