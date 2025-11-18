"""
symbolite.abstract.lang
~~~~~~~~~~~~~~~~~~~~~~~

Language-level symbolic primitives such as assignments and blocks.
"""

from __future__ import annotations

from typing import Any, NamedTuple

from symbolite.ops._get_name import get_name

from ..core.lang import ValueConverter
from ..core.symbolite_object import (
    SymboliteObject,
    set_symbolite_info,
)
from ..core.value import Value

to_bool = ValueConverter[bool]

to_int = ValueConverter[int]

to_float = ValueConverter[float]

to_tuple = ValueConverter[tuple[Any, ...]]

to_list = ValueConverter[list[Any]]

to_dict = ValueConverter[tuple[tuple[Any, Any], ...]]


class AssignInfo(NamedTuple):
    lhs: Value[Any]
    rhs: Any


class Assign(SymboliteObject[AssignInfo]):
    def __init__(self, lhs: Value[Any], rhs: Any) -> None:
        set_symbolite_info(self, AssignInfo(lhs, rhs))


class BlockInfo(NamedTuple):
    inputs: tuple[Value[Any], ...]
    outputs: tuple[Value[Any], ...]
    lines: tuple[Assign, ...]
    name: str = ""


class Block(SymboliteObject[BlockInfo]):
    """A block of code with inputs and outputs."""

    def __init__(
        self,
        inputs: tuple[Value[Any], ...],
        outputs: tuple[Value[Any], ...],
        lines: tuple[Assign, ...],
        *,
        name: str = "",
    ) -> None:
        set_symbolite_info(self, BlockInfo(inputs, outputs, lines, name))


@get_name.register
def get_name_block_info(obj: BlockInfo, qualified: bool = True) -> str:
    return obj.name or "__symbolite_block"


__all__ = [
    "Assign",
    "AssignInfo",
    "Block",
    "BlockInfo",
    "to_bool",
    "to_int",
    "to_float",
    "to_tuple",
    "to_list",
    "to_dict",
]
