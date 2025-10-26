import math

import pytest

from symbolite import Real, Symbol, real
from symbolite.core.symbolgroup import SymbolicNamespace
from symbolite.impl import libstd
from symbolite.ops import as_code, get_name, substitute
from symbolite.ops.base import symbol_names, translate


def test_double_naming():
    with pytest.warns(UserWarning):

        class N(SymbolicNamespace):
            x = Symbol("x")
            y = Symbol("z")


def test_naming():
    class N(SymbolicNamespace):
        x = Symbol()
        y = Symbol()

    assert isinstance(N.x, Symbol)
    assert isinstance(N.y, Symbol)
    x_name = get_name(N.x, qualified=False)
    y_name = get_name(N.y, qualified=False)
    assert x_name == "x"
    assert y_name == "y"
    assert symbol_names(N) == {"x", "y"}


def test_substitute_eval():
    class X(SymbolicNamespace):
        x = Real()
        y = Real()
        z = x + 2 * y
        p = real.cos(z)

    Y = substitute(X, {X.x: 1, X.y: 2})

    assert Y.x == 1
    assert Y.y == 2

    d = translate(Y, libstd)
    assert d["x"] == 1
    assert d["y"] == 2
    assert d["z"] == d["x"] + 2 * d["y"]
    assert d["p"] == math.cos(d["z"])


def test_as_code():
    class X(SymbolicNamespace):
        x = Real()
        y = Real()
        z = x + 2 * y
        # p = real.cos(z)

    s = "\n".join(
        [
            "# X",
            "",
            "x = Real()",
            "y = Real()",
            "",
            "z = x + 2 * y",
            # "p = real.cos(x + 2 * y)",
        ]
    )

    assert as_code(X) == s


@pytest.mark.skip(reason="Not implemented yet")
def test_eq():
    class N(SymbolicNamespace):
        x = Real()
        y = Real()

        eq = x.eq(2 * y)

    s = "\n".join(["# N", "", "x = Real()", "y = Real()", "", "eq = x == 2 * y"])

    assert as_code(N) == s
