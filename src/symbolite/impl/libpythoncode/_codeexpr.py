"""
symbolite.impl.libpythoncode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utilities to build Python source snippets from Symbolite expressions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import keyword
import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
from unicodedata import normalize

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


def validate_identifier(name: str, *, role: str = "identifier") -> str:
    """Validate and normalize a Python identifier before emitting source."""
    normalized = normalize("NFKC", name)
    if (
        not name.isidentifier()
        or keyword.iskeyword(normalized)
        or normalized == "__debug__"
    ):
        raise ValueError(f"Invalid Python {role}: {name!r}")
    return normalized


def validate_qualified_name(name: str) -> str:
    return ".".join(validate_identifier(part) for part in name.split("."))


def _coerce(value: Any) -> CodeExpr:
    if isinstance(value, CodeExpr):
        return value
    if isinstance(value, str):
        return CodeExpr(value)
    if isinstance(value, bool):
        return CodeExpr("True" if value else "False")
    if isinstance(value, float) and not math.isfinite(value):
        # Numeric syntax avoids global lookups, even if inputs are called
        # float, inf, or nan. Keep NaN grouped when used inside an operator.
        if math.isnan(value):
            return CodeExpr("(1e309 - 1e309)")
        if value < 0:
            return CodeExpr("-1e309", precedence=2)
        return CodeExpr("1e309")
    if isinstance(value, (int, float, complex)):
        text = repr(value)
        # A leading minus is unary syntax, including for negative zero.
        return CodeExpr(text, precedence=2 if text.startswith("-") else 100)
    return CodeExpr(str(value))


def _join_arguments(
    args: Iterable[CodeExpr], kwargs: Iterable[tuple[str, CodeExpr]]
) -> str:
    parts = [arg.text for arg in args]
    parts.extend(
        f"{validate_identifier(key, role='keyword argument')}={value.text}"
        for key, value in kwargs
    )
    return ", ".join(parts)


def _maybe_parenthesize(expr: CodeExpr, precedence: int, *, group_equal: bool) -> str:
    if expr.precedence < precedence:
        return f"({expr.text})"
    if group_equal and expr.precedence == precedence:
        return f"({expr.text})"
    return expr.text


def make_function(qualified_name: str) -> Any:
    qualified_name = validate_qualified_name(qualified_name)

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
    return CodeExpr(validate_qualified_name(name))


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
