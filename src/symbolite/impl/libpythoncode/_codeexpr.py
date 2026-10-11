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
from ...ops._get_name import get_full_name


@dataclass(frozen=True)
class CodeExpr:
    """Represents a snippet of Python code plus its precedence."""

    text: str
    precedence: int = 100

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.text


def _coerce(value: Any) -> CodeExpr:
    if isinstance(value, CodeExpr):
        return value
    if isinstance(value, str):
        return CodeExpr(value)
    if isinstance(value, bool):
        return CodeExpr("True" if value else "False")
    if isinstance(value, (int, float, complex)):
        text = repr(value)
        # A leading minus is unary syntax, including for negative zero.
        return CodeExpr(text, precedence=2 if text.startswith("-") else 100)
    return CodeExpr(str(value))


def _join_arguments(
    args: Iterable[CodeExpr], kwargs: Iterable[tuple[str, CodeExpr]]
) -> str:
    parts = [arg.text for arg in args]
    parts.extend(f"{key}={value.text}" for key, value in kwargs)
    return ", ".join(parts)


def _maybe_parenthesize(expr: CodeExpr, precedence: int, *, group_equal: bool) -> str:
    if expr.precedence < precedence:
        return f"({expr.text})"
    if group_equal and expr.precedence == precedence:
        return f"({expr.text})"
    return expr.text


def make_function(qualified_name: str) -> Any:
    def _function(*args: Any, **kwargs: Any) -> CodeExpr:
        coerced_args = tuple(_coerce(arg) for arg in args)
        coerced_kwargs = tuple((k, _coerce(v)) for k, v in kwargs.items())
        return CodeExpr(
            f"{qualified_name}({_join_arguments(coerced_args, coerced_kwargs)})"
        )

    return _function


def make_operator(
    fmt: str, precedence: int, arity: int, *, right_associative: bool = False
) -> Any:
    def _operator(*args: Any) -> CodeExpr:
        coerced = tuple(_coerce(arg) for arg in args)
        if arity == 1:
            (value,) = coerced
            formatted = fmt.format(
                _maybe_parenthesize(value, precedence, group_equal=False)
            )
        else:
            leading = coerced[0]
            trailing = coerced[1:]
            formatted_args = [
                _maybe_parenthesize(leading, precedence, group_equal=right_associative),
                *(
                    _maybe_parenthesize(
                        arg,
                        precedence,
                        group_equal=not right_associative
                        and index == len(trailing) - 1,
                    )
                    for index, arg in enumerate(trailing)
                ),
            ]
            formatted = fmt.format(*formatted_args)
        return CodeExpr(formatted, precedence)

    return _operator


def make_attribute(name: str) -> CodeExpr:
    return CodeExpr(name)


def as_function(obj: Function[Any] | Operator[Any]) -> Any:
    qualified_name = get_full_name(obj)
    return make_function(qualified_name)


def as_operator(obj: Operator[Any]) -> Any:
    info = get_symbolite_info(obj)
    return make_operator(
        info.fmt,
        info.precedence,
        info.arity,
        right_associative=info.fmt == "{} ** {}",
    )


def as_named_value(obj: Value[Any]) -> CodeExpr:
    info = get_symbolite_info(obj)
    if not isinstance(info.value, Name):
        raise TypeError(f"Value {obj!r} is not bound to a Name.")
    qualified_name = get_full_name(obj)
    return make_attribute(qualified_name)
