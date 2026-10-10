from collections.abc import Callable

import pytest

from symbolite import Real, substitute, translate
from symbolite.impl import liblatex
from symbolite.impl.liblatex._latexexpr import LatexExpr

x, y, z = map(Real, ["x", "y", "z"])
dummy_reals = (x, y, z)

all_funcs = {impl: getattr(liblatex.real, impl) for impl in liblatex.real.__all__}


@pytest.mark.parametrize("func", all_funcs.values(), ids=all_funcs.keys())
def test_all_real_funcs_run(func: Callable | LatexExpr):
    if func == liblatex.real.Real:
        assert isinstance(func("x"), LatexExpr)
        return
    # TODO: set what each function should be tested as
    try:
        # Test as unary function
        func(*dummy_reals[:1])
    except IndexError:
        # Test as binary function
        func(*dummy_reals[:2])
    except TypeError:
        # Test as named value
        assert isinstance(func, LatexExpr)


@pytest.mark.parametrize(
    "expr,expected",
    [
        ((x**y) ** z, r"\left(x^{y}\right)^{z}"),
        (x ** (y**z), r"x^{y^{z}}"),
        (Real(-2) ** x, r"\left(-2\right)^{x}"),
        (Real(-2.5) ** x, r"\left(-2.5\right)^{x}"),
        (Real(-0.0) ** x, r"\left(-0.0\right)^{x}"),
        (substitute(x**y, {x: -2, y: 2}), r"\left(-2\right)^{2}"),
        (-(x**y), r"-x^{y}"),
        ((-x) ** y, r"\left(-x\right)^{y}"),
        (x ** (-y), r"x^{\left(-y\right)}"),
    ],
)
def test_power_grouping_and_signed_literals(expr: Real, expected: str):
    assert str(translate(expr, liblatex)) == expected
