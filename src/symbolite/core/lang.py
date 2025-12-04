"""
symbolite.core.lang
~~~~~~~~~~~~~~~~~~~

Language related primitives.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from typing import Any, NamedTuple

from .symbolite_object import SymboliteObject, get_symbolite_info, set_symbolite_info
from .value import Value


class ValueConverter[T]:
    def __call__(self, value: T, libsl: types.ModuleType) -> Any:
        return value


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
        content = tuple(lines)
        binfo = BlockInfo(inputs, outputs, content, name)
        _validate_block_dependencies(binfo)
        set_symbolite_info(self, binfo)


def _validate_block_dependencies(info: BlockInfo) -> None:
    from ..ops._get_name import get_full_name
    from ..ops.base import free_values

    defined = {get_full_name(var) for var in info.inputs}

    for line_number, assign in enumerate(info.lines, start=1):
        ainfo = get_symbolite_info(assign)
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
