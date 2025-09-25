import pytest

from symbolite import Scalar, scalar
from symbolite.ops import as_string

x, y, z = map(scalar.Scalar, "x y z".split())


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y * z, "x + y * z"),
        ((x + y) * z, "(x + y) * z"),
        (x * y + z, "x * y + z"),
        (x * (y + z), "x * (y + z)"),
        (-(x**y), "-x ** y"),
        ((-x) ** y, "(-x) ** y"),
    ],
)
def test_different_precedence(expr: Scalar, result: Scalar):
    assert as_string(expr) == result
    assert str(expr) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y + z, "x + y + z"),
        ((x + y) + z, "x + y + z"),
        (x + (y + z), "x + (y + z)"),  # Python is not associative
    ],
)
def test_same_precedence(expr: Scalar, result: Scalar):
    assert as_string(expr) == result
    assert str(expr) == result
