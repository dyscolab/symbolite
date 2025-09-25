import pytest

from symbolite import Scalar, scalar
from symbolite.ops import as_string

x, y, z = map(scalar.Scalar, "x y z".split())


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y, "x + y"),
        (x - y, "x - y"),
        (x * y, "x * y"),
        (x / y, "x / y"),
        (x**y, "x ** y"),
        (x // y, "x // y"),
        (((x**y) % z), "x ** y % z"),
    ],
)
def test_known_symbols(expr: Scalar, result: Scalar):
    assert as_string(expr) == result
    assert str(expr) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + scalar.cos(y), "x + scalar.cos(y)"),
        (x + scalar.pi, "x + scalar.pi"),
    ],
)
def test_lib_symbols(expr: Scalar, result: Scalar):
    assert as_string(expr) == result
