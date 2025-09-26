import types
from typing import Any

import pytest

from symbolite import Symbol, real, vector
from symbolite.core import Unsupported
from symbolite.impl import get_all_implementations
from symbolite.ops import substitute
from symbolite.ops.base import evaluate, symbol_names

all_impl = get_all_implementations()

x, y = map(real.Real, ("x", "y"))
vec = vector.Vector("vec")
v = vector.Vector("v")

xsy = Symbol("xsy")

requires_numpy = pytest.mark.skipif("libnumpy" not in all_impl, reason="Requires NumPy")
requires_sympy = pytest.mark.skipif("libsympy" not in all_impl, reason="Requires SymPy")


@pytest.mark.mypy_testing
# noqa: F821
def test_typing():
    reveal_type(v + v)  # R: symbolite.abstract.vector.Vector # noqa: F821
    reveal_type(2 + v)  # R: symbolite.abstract.vector.Vector # noqa: F821
    reveal_type(v + 2)  # R: symbolite.abstract.vector.Vector # noqa: F821
    # reveal_type(v + xsy) # R: symbolite.abstract.vector.Vector # noqa: F821
    # reveal_type(xsy + v)  # R: symbolite.abstract.vector.Vector # noqa: F821
    reveal_type(vec[0])  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(vec[x])  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(vector.sum(vec))  # R: symbolite.abstract.real.Real # noqa: F821


def test_vector():
    assert str(vec) == "vec"
    assert str(vec[1]) == "vec[1]"


def test_methods():
    assert substitute(vec, {vec: (1, 2, 3)}) == (1, 2, 3)
    assert evaluate(substitute(vec[1], {vec: (1, 2, 3)})) == 2
    assert symbol_names(vec) == {
        "vec",
    }
    assert symbol_names(vec[1]) == {
        "vec",
    }
    assert symbol_names(vec[1] + vec[0]) == {
        "vec",
    }


@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_impl(libsl: types.ModuleType):
    v = vector.Vector("v")

    v1234 = (1, 2, 3, 4)
    try:
        import numpy as np  # type: ignore

        v1234 = np.asarray(v1234)  # type: ignore
    except ImportError:
        pass

    try:
        expr = vector.sum(v)
        assert evaluate(substitute(expr, {v: v1234}), libsl=libsl) == 10
    except Unsupported:
        pass

    expr = vector.prod(v)
    assert evaluate(substitute(expr, {v: v1234}), libsl=libsl) == 24


@requires_numpy
def test_impl_numpy():
    try:
        import numpy as np  # type: ignore

        from symbolite.impl import libnumpy as libsl
    except ImportError:
        return

    v = np.asarray((1, 2, 3))

    expr1 = vector.Vector("vec") + 1
    assert np.allclose(evaluate(substitute(expr1, {vec: v})), v + 1)

    expr2 = real.cos(vector.sum(vector.Vector("vec")))

    assert np.allclose(
        evaluate(substitute(expr2, {vec: v}), libsl=libsl), np.cos(np.sum(v))
    )


@requires_sympy
def test_impl_sympy():
    try:
        import sympy as sy  # type: ignore

        from symbolite.impl import libsympy as libsl
    except ImportError:
        return

    vec = vector.Vector("vec")
    syarr = sy.IndexedBase("vec")
    assert evaluate(vec, libsl=libsl) == syarr
    assert evaluate(vec[1], libsl=libsl) == syarr[1]


@pytest.mark.parametrize(
    "expr,params,result",
    [
        (x + 2 * y, ("x", "y"), vec[0] + 2 * vec[1]),
        (x + 2 * y, ("y", "x"), vec[1] + 2 * vec[0]),
        (x + 2 * real.cos(y), ("y", "x"), vec[1] + 2 * real.cos(vec[0])),
        (x + 2 * y, dict(x=3, y=5), vec[3] + 2 * vec[5]),
        (x + 2 * y, dict(x=5, y=3), vec[5] + 2 * vec[3]),
    ],
)
def test_vectorize(expr: vector.Vector, params: Any, result: Symbol):
    assert vector.vectorize(expr, params) == result


def test_vectorize_non_default_varname():
    assert vector.vectorize(x + 2 * y, ("x", "y"), varname="v") == v[0] + 2 * v[1]


def test_vectorize_many():
    eqs = [
        x + 2 * y,
        y + 3 * x,
    ]
    result = (
        vec[2] + 2 * vec[0],
        vec[0] + 3 * vec[2],
    )
    assert vector.vectorize(eqs, ("y", "z", "x")) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + 2 * y, (("x", "y"), vec[0] + 2 * vec[1])),
        (y + 2 * x, (("x", "y"), vec[1] + 2 * vec[0])),
        (x + 2 * real.cos(y), (("x", "y"), vec[0] + 2 * real.cos(vec[1]))),
    ],
)
def test_autovectorize(expr: Symbol, result: Symbol):
    assert vector.auto_vectorize(expr) == result


def test_autovectorize_non_default_varname():
    assert vector.auto_vectorize(x + 2 * y, "v") == (("x", "y"), v[0] + 2 * v[1])


def test_autovectorize_many():
    eqs = [
        x + 2 * y,
        y + 3 * x,
    ]
    result = (
        vec[0] + 2 * vec[1],
        vec[1] + 3 * vec[0],
    )
    assert vector.auto_vectorize(eqs) == (("x", "y"), result)
