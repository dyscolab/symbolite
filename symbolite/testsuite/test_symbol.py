from typing import Any

import pytest

from symbolite import Symbol
from symbolite.core.call import Call
from symbolite.core.function import UserFunction
from symbolite.core.symbolite_object import get_symbolite_info
from symbolite.impl import find_module_in_stack, libpythoncode
from symbolite.impl.libpythoncode._codeexpr import make_function
from symbolite.ops import substitute
from symbolite.ops._as_code import as_code
from symbolite.ops.base import evaluate, symbol_names

x, y, z = map(Symbol, "x y z".split())

F = UserFunction("F", output_type=Symbol)  # type: ignore
G = UserFunction("G", output_type=Symbol)  # type: ignore

F.register_impl(make_function("F"), libsl=libpythoncode)  # type: ignore
G.register_impl(make_function("G"), libsl=libpythoncode)  # type: ignore


@pytest.mark.mypy_testing
def test_typing():
    reveal_type(x + y)  # R: symbolite.abstract.symbol.Symbol # noqa: F821
    reveal_type(2 + y)  # R: symbolite.abstract.symbol.Symbol # noqa: F821
    reveal_type(x + 2)  # R: symbolite.abstract.symbol.Symbol # noqa: F821


def _helper_forward_reverse(expr: Symbol) -> tuple[Any, ...]:
    expr_info = get_symbolite_info(expr)
    assert isinstance(expr_info.value, Call)
    call_info = get_symbolite_info(expr_info.value)
    func_info = get_symbolite_info(call_info.func)  # type: ignore
    assert func_info.name == "add"  # type: ignore
    return call_info.args


def test_forward_reverse():
    assert _helper_forward_reverse(x + 1) == (x, 1)
    assert _helper_forward_reverse(1 + x) == (1, x)


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
        (pow(x, y, z), "symbol.pow3(x, y, z)"),
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
def test_code(expr: Symbol, result: Symbol):
    assert as_code(expr) == result


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


class Real(Symbol):
    pass


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + 2 * y, 1 + 2 * 3),
        # (x + 2 * F(y), x + 2 * F(z)),
    ],
)
def test_eval_str(expr: Symbol, result: Symbol):
    assert eval(as_code(substitute(expr, {x: 1, y: 3}))) == result


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + 2 * y, 1 + 2 * 3),
        # (x + 2 * F(y), x + 2 * F(z)),
    ],
)
def test_evaluate(expr: Symbol, result: Symbol):
    assert evaluate(substitute(expr, {x: 1, y: 3})) == result


def test_find_libs_in_stack():
    assert find_module_in_stack() is None
    from symbolite.impl import libstd as libsl  # noqa: F401

    assert find_module_in_stack()
