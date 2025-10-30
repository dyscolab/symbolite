import pytest

from symbolite import Real, real
from symbolite.ops import as_code

x, y, z = map(real.Real, "x y z".split())


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
def test_known_symbols(expr: Real, result: Real):
    assert as_code(expr) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + real.cos(y), "x + real.cos(y)"),
        (x + real.pi, "x + real.pi"),
    ],
)
def test_lib_symbols(expr: Real, result: Real):
    assert as_code(expr) == result
