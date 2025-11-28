"""
symbolite.abstract.lang
~~~~~~~~~~~~~~~~~~~~~~~

Language-level symbolic primitives such as assignments and blocks.
"""

from __future__ import annotations

from typing import Any

from symbolite.ops._get_name import get_name

from ..core.lang import AssignInfo, BlockInfo, ValueConverter
from ..core.symbolite_object import (
    SymboliteObject,
    get_symbolite_info,
    set_symbolite_info,
)
from ..core.value import Value
from ..ops._get_name import get_full_name
from ..ops.base import free_values

to_bool = ValueConverter[bool]()

to_int = ValueConverter[int]()

to_float = ValueConverter[float]()

to_tuple = ValueConverter[tuple[Any, ...]]()

to_list = ValueConverter[list[Any]]()

to_dict = ValueConverter[tuple[tuple[Any, Any], ...]]()


def _validate_block_dependencies(info: BlockInfo) -> None:
    defined = {get_full_name(var) for var in info.inputs}

    for line_number, ainfo in enumerate(info.lines, start=1):
        for var in free_values(ainfo.rhs):
            name = get_full_name(var)
            if name not in defined:
                raise ValueError(
                    f"Block line {line_number}: value '{name}' must be provided as an input or defined in a previous line."
                )

        defined.add(get_full_name(ainfo.lhs))

    for output in info.outputs:
        name = get_full_name(output)
        if name not in defined:
            raise ValueError(
                f"Block output value '{name}' must be provided as an input or defined in the block body."
            )


class Assign(SymboliteObject[AssignInfo]):
    def __init__(self, lhs: Value[Any], rhs: Any) -> None:
        set_symbolite_info(self, AssignInfo(lhs, rhs))


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
        content = tuple(get_symbolite_info(obj) for obj in lines)
        binfo = BlockInfo(inputs, outputs, content, name)
        _validate_block_dependencies(binfo)
        set_symbolite_info(self, binfo)


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
