"""
symbolite.impl.libpythoncode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utilities to build Python source snippets from Symbolite expressions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from ...core.function import Function, Operator
from ...core.symbolite_object import get_symbolite_info
from ...core.value import Name, Value
from ._latex_names import _get_latex_name, _get_latex_precedence, _parenthesize


@dataclass(frozen=True)
class LatexExpr:
    """Represents a snippet of Python code plus its precedence."""

    text: str
    precedence: int = 100

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.text


def _coerce(value: Any) -> LatexExpr:
    if isinstance(value, LatexExpr):
        return value
    if isinstance(value, str):
        return LatexExpr(value)
    if isinstance(value, bool):
        return LatexExpr("True" if value else "False")
    if isinstance(value, (int, float, complex)):
        return LatexExpr(repr(value))
    return LatexExpr(str(value))


def _join_arguments(
    args: Iterable[LatexExpr], kwargs: Iterable[tuple[str, LatexExpr]]
) -> str:
    parts = [arg.text for arg in args]
    parts.extend(f"{key}={value.text}" for key, value in kwargs)
    return ", ".join(parts)


def _maybe_parenthesize(
    expr: LatexExpr, precedence: int, *, right: bool, parenthesize: bool
) -> str:
    if expr.precedence < precedence and parenthesize:
        return f"\\left({expr.text}\\right)"
    if right and expr.precedence == precedence and parenthesize:
        return f"\\left({expr.text}\\right)"
    return expr.text


def make_function(latex_name: str) -> Any:
    def _function(*args: Any, **kwargs: Any) -> LatexExpr:
        coerced_args = tuple(_coerce(arg) for arg in args)
        coerced_kwargs = tuple((k, _coerce(v)) for k, v in kwargs.items())
        return LatexExpr(
            f"{latex_name}\\left( {_join_arguments(coerced_args, coerced_kwargs)} \\right)"
        )

    return _function


def make_operator(fmt: str, precedence: int, arity: int, parenthesize: bool) -> Any:
    def _operator(*args: Any) -> LatexExpr:
        coerced = tuple(_coerce(arg) for arg in args)
        if arity == 1:
            (value,) = coerced
            formatted = fmt.format(
                _maybe_parenthesize(
                    value,
                    precedence,
                    right=False,
                    parenthesize=parenthesize,
                )
            )
        else:
            leading = coerced[0]
            trailing = coerced[1:]
            formatted_args = [
                _maybe_parenthesize(
                    leading,
                    precedence,
                    right=False,
                    parenthesize=parenthesize,
                ),
                *(
                    _maybe_parenthesize(
                        arg,
                        precedence,
                        right=index == len(trailing) - 1,
                        parenthesize=parenthesize,
                    )
                    for index, arg in enumerate(trailing)
                ),
            ]
            formatted = fmt.format(*formatted_args)
        return LatexExpr(formatted, precedence)

    return _operator


def make_attribute(name: str) -> LatexExpr:
    return LatexExpr(name)


def as_function(obj: Function[Any]) -> Any:
    latex_name = _get_latex_name(obj)
    return make_function(latex_name)


def as_operator(obj: Operator[Any]) -> Any:
    info = get_symbolite_info(obj)
    return make_operator(
        _get_latex_name(obj),
        _get_latex_precedence(obj),
        info.arity,
        parenthesize=_parenthesize(obj),
    )


def as_named_value(obj: Value[Any]) -> LatexExpr:
    info = get_symbolite_info(obj)
    if not isinstance(info.value, Name):
        raise TypeError(f"Value {obj!r} is not bound to a Name.")
    latex_name = _get_latex_name(obj)
    return make_attribute(latex_name)


def _nest_with_brackets(text: str, separator: str) -> str:
    parts = text.split(separator)

    result = parts[-1]

    for part in reversed(parts[:-1]):
        result = f"{part}{separator}{{{result}}}"

    return result


def nest_sub_and_super_scripts(text: str) -> str:
    return _nest_with_brackets(_nest_with_brackets(text, "_"), "^")
