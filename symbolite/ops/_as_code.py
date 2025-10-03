"""
symbolite.core.ops._as_code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert a symbolite object to python code.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from functools import singledispatch
from typing import Any

from symbolite.core.call import Call
from symbolite.core.function import (
    BinaryOperator,
    Function,
    UnaryOperator,
)

from ..core import SymbolicNamespace, SymbolicNamespaceMeta, Variable
from ..core.symbolite_object import get_symbolite_info
from ..core.variable import Name
from ._get_name import get_name
from .base import assign, free_variables


def _resolve_precedence(
    other: Any,
) -> tuple[int, Call] | None:
    """Return operator precedence for the outer expression, if available."""

    if isinstance(other, Call):
        expr = other
    elif isinstance(other, Variable) and not isinstance(
        get_symbolite_info(other).value, Name
    ):
        expr = get_symbolite_info(other).value
    else:
        return None

    info = get_symbolite_info(expr)
    func = info.func
    if isinstance(func, (UnaryOperator, BinaryOperator)):
        info_func = get_symbolite_info(func)
        return info_func.precedence, expr
    return None


def _add_parenthesis(
    self: UnaryOperator[Any, Any] | BinaryOperator[Any, Any, Any],
    other: Any,
    *,
    right: bool,
) -> str:
    resolved = _resolve_precedence(other)
    self_fields = get_symbolite_info(self)
    if resolved is not None:
        precedence, _ = resolved
        if precedence < self_fields.precedence or (
            right and precedence <= self_fields.precedence
        ):
            return f"({as_code(other)})"
    return as_code(other)


@singledispatch
def as_calling_code(
    obj: Any, args: tuple[Any, ...], kwargs_items: tuple[tuple[str, Any], ...]
) -> str:
    """Convert a symbolite object to python code."""
    raise Exception(f"as_calling_code not implemented for {type(obj)}")


@as_calling_code.register(Function)
def as_calling_code_func(
    obj: Function[Any], args: tuple[Any, ...], kwargs_items: tuple[tuple[str, Any], ...]
) -> str:
    plain_args = tuple(map(as_code, args)) + tuple(
        f"{k}={as_code(v)}" for k, v in kwargs_items
    )
    return f"{get_name(obj, qualified=True)}({', '.join((v for v in plain_args))})"


@as_calling_code.register(UnaryOperator)
def as_calling_code_unop(
    obj: UnaryOperator[Any, Any],
    args: tuple[Any, ...],
    _kwargs_items: tuple[tuple[str, Any], ...],
) -> str:
    (x,) = args
    x = _add_parenthesis(obj, x, right=False)
    info = get_symbolite_info(obj)
    return info.fmt.format(x)


@as_calling_code.register(BinaryOperator)
def as_calling_code_binop(
    obj: BinaryOperator[Any, Any, Any],
    args: tuple[Any, ...],
    _kwargs_items: tuple[tuple[str, Any], ...],
) -> str:
    (x, y) = args
    x = _add_parenthesis(obj, x, right=False)
    y = _add_parenthesis(obj, y, right=True)
    info = get_symbolite_info(obj)
    return info.fmt.format(x, y)


@singledispatch
def as_code(obj: Any) -> str:
    """Convert a symbolite object to python code."""
    raise Exception(f"as_code not implemented for {type(obj)}")


@as_code.register
def as_code_str_fallback(obj: int | float) -> str:
    """Convert a symbolite object to python code."""
    return str(obj)


@as_code.register(Variable)
def as_code_variable(obj: Variable[Any]) -> str:
    info = get_symbolite_info(obj)
    if isinstance(info.value, Name):
        return get_name(info.value)
    return as_code(info.value)


@as_code.register
def as_code_call(obj: Call) -> str:
    info = get_symbolite_info(obj)
    return as_calling_code(info.func, info.args, info.kwargs_items)


@as_code.register
def _(obj: SymbolicNamespaceMeta | SymbolicNamespace) -> str:
    lines = [f"# {obj.__name__}", ""]

    for fs in free_variables(obj):
        fs_name = get_name(fs, qualified=False)
        lines.append(assign(fs_name or "<anonymous>", f"{fs.__class__.__name__}()"))

    lines.append("")

    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if not isinstance(attr, Variable):
            continue

        info = get_symbolite_info(attr)
        if isinstance(info.value, Name):
            continue
        lines.append(assign(attr_name, as_code(info.value)))

    return "\n".join(lines)
