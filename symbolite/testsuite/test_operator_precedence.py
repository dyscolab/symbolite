import pytest

from symbolite import Real, real
from symbolite.ops import as_code

x, y, z = map(real.Real, "x y z".split())


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
def test_different_precedence(expr: Real, result: str):
    assert as_code(expr) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y + z, "x + y + z"),
        ((x + y) + z, "x + y + z"),
        (x + (y + z), "x + (y + z)"),  # Python is not associative
    ],
)
def test_same_precedence(expr: Real, result: str):
    assert as_code(expr) == result
