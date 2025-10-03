"""
symbolite.core.ops._as_code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert a symbolite object to python code.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from functools import singledispatch
from typing import Any

from symbolite.core.expression import Expression, Named
from symbolite.core.function import (
    BinaryOperator,
    NamedExpression,
    UnaryOperator,
)

from ..abstract import Real, Symbol, Vector
from ..core import SymbolicNamespace, SymbolicNamespaceMeta
from .base import assign, free_symbols


def _resolve_precedence(
    other: Any,
) -> tuple[int, Expression[Any]] | None:
    """Return operator precedence for the outer expression, if available."""

    if isinstance(other, Expression):
        expr = other
    elif isinstance(other, NamedExpression) and other.expression is not None:
        expr = other.expression
    else:
        return None

    func = expr.func
    if isinstance(func, (UnaryOperator, BinaryOperator)):
        return func.precedence, expr
    return None


def _add_parenthesis(
    self: UnaryOperator[Any, Any] | BinaryOperator[Any, Any],
    other: Any,
    *,
    right: bool,
) -> str:
    resolved = _resolve_precedence(other)
    if resolved is not None:
        precedence, _ = resolved
        if precedence < self.precedence or (right and precedence <= self.precedence):
            return f"({as_code(other)})"
    return as_code(other)


@singledispatch
def as_code(expr: Any) -> str:
    """Convert a symbolite object to python code."""
    return str(expr)


@as_code.register
def as_code_named(obj: Named) -> str:
    if obj.name is None:
        return "<anonymous>"
    if obj.namespace:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@as_code.register
def _(obj: NamedExpression) -> str:
    if obj.expression is None:
        return as_code_named(obj)
    return as_code(obj.expression)


@as_code.register
def _(obj: Expression) -> str:
    func = obj.func
    if func.fmt is None:
        plain_args = tuple(map(as_code, obj.args)) + tuple(
            f"{k}={as_code(v)}" for k, v in obj.kwargs.items()
        )
        return f"{as_code(func)}({', '.join((v for v in plain_args))})"

    if isinstance(func, BinaryOperator):
        x, y = obj.args
        x = _add_parenthesis(func, x, right=False)
        y = _add_parenthesis(func, y, right=True)
        return func.fmt.format(x, y)
    elif isinstance(func, UnaryOperator):
        (x,) = obj.args
        x = _add_parenthesis(func, x, right=False)
        return func.fmt.format(x)
    else:
        return func.fmt.format(
            *map(as_code, obj.args),
            **{k: as_code(v) for k, v in obj.kwargs.items()},
        )


@as_code.register
def _(obj: SymbolicNamespaceMeta | SymbolicNamespace) -> str:
    lines = [f"# {obj.__name__}", ""]

    for fs in free_symbols(obj):
        lines.append(assign(fs.name, f"{fs.__class__.__name__}()"))

    lines.append("")

    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if not isinstance(attr, (Symbol, Real, Vector)):
            continue

        if attr.expression is not None:
            lines.append(assign(attr_name, f"{attr!s}"))

    return "\n".join(lines)
