import math

import pytest

from symbolite import Real, Symbol, real, substitute, translate
from symbolite.core.lang import Assign, Block
from symbolite.impl import libstd
from symbolite.ops import as_code

x, y, z = map(real.Real, ["x", "y", "z"])


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y * z, "x + y * z"),
        ((x + y) * z, "(x + y) * z"),
        (x * y + z, "x * y + z"),
        (x * (y + z), "x * (y + z)"),
        (-(x**y), "-x ** y"),
        ((-x) ** y, "(-x) ** y"),
        (Real(-2) ** x, "(-2) ** x"),
        (Real(-2.5) ** x, "(-2.5) ** x"),
        (Real(-0.0) ** x, "(-0.0) ** x"),
        (x ** (-y), "x ** (-y)"),
    ],
)
def test_different_precedence(expr: Real, result: str):
    assert as_code(expr) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        ((x + y) + z, "x + y + z"),
        (x + (y + z), "x + (y + z)"),  # Python is not associative
        ((x**y) ** z, "(x ** y) ** z"),
        (x ** (y**z), "x ** y ** z"),
    ],
)
def test_same_precedence(expr: Real, result: str):
    assert as_code(expr) == result


@pytest.mark.parametrize("cls", [Real, Symbol])
@pytest.mark.parametrize(
    "expression,values,expected",
    [
        pytest.param(lambda x, y, z: (x**y) ** z, (2, 3, 2), 64, id="left-power"),
        pytest.param(lambda x, y, z: x ** (y**z), (2, 3, 2), 512, id="right-power"),
        pytest.param(lambda x, y, z: (-x) ** y, (2, 2, 1), 4, id="negative-base"),
        pytest.param(lambda x, y, z: -(x**y), (2, 2, 1), -4, id="negated-power"),
        pytest.param(
            lambda x, y, z: type(x)(-2) ** y,
            (1, 2, 1),
            4,
            id="negative-int-literal",
        ),
        pytest.param(
            lambda x, y, z: type(x)(-2.5) ** y,
            (1, 2, 1),
            6.25,
            id="negative-float-literal",
        ),
        pytest.param(
            lambda x, y, z: x ** (-y), (2, 2, 1), 0.25, id="negative-exponent"
        ),
        pytest.param(
            lambda x, y, z: type(x)(-2) ** (-y),
            (1, 2, 1),
            0.25,
            id="negative-base-and-exponent",
        ),
        pytest.param(
            lambda x, y, z: (type(x)(-2) ** y) ** z,
            (1, 3, 2),
            64,
            id="nested-negative-base",
        ),
        pytest.param(
            lambda x, y, z: x ** (y ** (-z)),
            (16, 2, 2),
            2,
            id="nested-negative-exponent",
        ),
    ],
)
def test_generated_power_semantics(cls, expression, values, expected):
    x, y, z, result = map(cls, ("x", "y", "z", "result"))
    expr = expression(x, y, z)
    resolved = substitute(expr, dict(zip((x, y, z), values)))
    assert translate(resolved, libstd) == pytest.approx(expected)

    block = Block((x, y, z), (result,), (Assign(result, expr),))
    assert translate(block, libstd)(*values) == pytest.approx(expected)

    # Substituted inputs become literals before source generation.
    literal_block = Block((), (result,), (Assign(result, resolved),))
    assert translate(literal_block, libstd)() == pytest.approx(expected)


@pytest.mark.parametrize("cls", [Real, Symbol])
@pytest.mark.parametrize("exponent,sign", [(1, -1), (2, 1)])
def test_generated_negative_zero_power(cls, exponent: int, sign: int):
    x, result = cls("x"), cls("result")
    block = Block((x,), (result,), (Assign(result, cls(-0.0) ** x),))
    value = translate(block, libstd)(exponent)
    assert value == 0
    assert math.copysign(1, value) == sign
