from __future__ import annotations

from typing import Any

from ...core import Unsupported
from ._latexexpr import LatexExpr, _coerce

Block = Unsupported

Assign = Unsupported


def to_bool(value: bool, libsl: Any) -> str:
    return "True" if value else "False"


def to_int(value: int, libsl: Any) -> LatexExpr:
    return _coerce(value)


def to_float(value: float, libsl: Any) -> LatexExpr:
    return _coerce(value)


def to_tuple(value: tuple[Any, ...], libsl: Any) -> str:
    return f"({', '.join(map(str, value))}, )"


def to_list(value: tuple[Any, ...], libsl: Any) -> str:
    return f"[{', '.join(map(str, value))}]"


def to_dict(value: tuple[tuple[Any, Any], ...], libsl: Any) -> str:
    items = to_tuple(tuple(to_tuple(pair, libsl) for pair in value), libsl)
    return f"dict({items})"


__all__ = [
    "Assign",
    "Block",
    "to_bool",
    "to_dict",
    "to_float",
    "to_int",
    "to_list",
    "to_tuple",
]
