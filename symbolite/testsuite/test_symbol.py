import pytest

from symbolite import Symbol
from symbolite.abstract.symbol import PythonFunction
from symbolite.core.expression import Expression
from symbolite.impl import find_module_in_stack
from symbolite.ops import substitute
from symbolite.ops.base import evaluate, symbol_names

x, y, z = map(Symbol, "x y z".split())

F = PythonFunction("F", arity=1)
G = PythonFunction("G", arity=1)


@pytest.mark.mypy_testing
# noqa: F821
def test_typing():
    reveal_type(x + y)  # R: symbolite.abstract.symbol.Symbol # noqa: F821
    reveal_type(2 + y)  # R: symbolite.abstract.symbol.Symbol # noqa: F821
    reveal_type(x + 2)  # R: symbolite.abstract.symbol.Symbol # noqa: F821


def test_forward_reverse():
    expr = x + 1
    assert isinstance(expr.expression, Expression)
    assert expr.expression.func.name == "add"
    assert expr.expression.args == (x, 1)

    expr = 1 + x
    assert isinstance(expr.expression, Expression)
    assert expr.expression.func.name == "add"
    assert expr.expression.args == (1, x)


@pytest.mark.parametrize(
    "expr,result",
    [
        (x < y, "x < y"),
        (x <= y, "x <= y"),
        (x > y, "x > y"),
        (x >= y, "x >= y"),
        (x[1], "x[1]"),
        (x[z], "x[z]"),
        (x + y, "x + y"),
        (x - y, "x - y"),
        (x * y, "x * y"),
        (x @ y, "x @ y"),
        (x / y, "x / y"),
        (x // y, "x // y"),
        (x % y, "x % y"),
        (x**y, "x ** y"),
        (x**y % z, "x ** y % z"),
        (pow(x, y, z), "pow(x, y, z)"),
        (x << y, "x << y"),
        (x >> y, "x >> y"),
        (x & y, "x & y"),
        (x ^ y, "x ^ y"),
        (x | y, "x | y"),
        # Reverse
        (1 + y, "1 + y"),
        (1 - y, "1 - y"),
        (1 * y, "1 * y"),
        (1 @ y, "1 @ y"),
        (1 / y, "1 / y"),
        (1 // y, "1 // y"),
        (1 % y, "1 % y"),
        (1**y, "1 ** y"),
        (1 << y, "1 << y"),
        (1 >> y, "1 >> y"),
        (1 & y, "1 & y"),
        (1 ^ y, "1 ^ y"),
        (1 | y, "1 | y"),
        (-x, "-x"),
        (+x, "+x"),
        (~x, "~x"),
        (F(x), "F(x)"),
        (G(x), "G(x)"),
    ],
)
def test_str(expr: Symbol, result: Symbol):
    assert str(expr) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + 2 * y, x + 2 * z),
        (x + 2 * F(y), x + 2 * F(z)),
    ],
)
def test_subs(expr: Symbol, result: Symbol):
    assert substitute(expr, {y: z}) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y, {"x", "y"}),
        (x[z], {"x", "z"}),
        (F(x), {"F", "x"}),
        (G(x), {"G", "x"}),
    ],
)
def test_symbol_names(expr: Symbol, result: set[str]):
    assert symbol_names(expr) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y, {"x", "y", "symbol.add"}),
        (x[z], {"x", "z", "symbol.getitem"}),
        (F(x), {"F", "x"}),
        (G(x), {"x", "G"}),
    ],
)
def test_symbol_names_ops(expr: Symbol, result: set[str]):
    assert symbol_names(expr, None) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + y, set()),
        (x[z], set()),
        (F(x), set()),
        (
            G(x),
            set(),
        ),
    ],
)
def test_symbol_names_namespace(expr: Symbol, result: Symbol):
    assert symbol_names(expr, namespace="lib") == result


class Scalar(Symbol):
    pass


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + 2 * y, 1 + 2 * 3),
        # (x + 2 * F(y), x + 2 * F(z)),
    ],
)
def test_eval_str(expr: Symbol, result: Symbol):
    assert eval(str(substitute(expr, {x: 1, y: 3}))) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + 2 * y, 1 + 2 * 3),
        # (x + 2 * F(y), x + 2 * F(z)),
    ],
)
def test_eval(expr: Symbol, result: Symbol):
    assert evaluate(substitute(expr, {x: 1, y: 3})) == result


def test_find_libs_in_stack():
    assert find_module_in_stack() is None
    from symbolite.impl import libstd as libsl  # noqa: F401

    assert find_module_in_stack()
