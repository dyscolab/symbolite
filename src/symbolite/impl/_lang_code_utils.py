"""
Shared utilities to translate language-level constructs such as blocks.
"""

from __future__ import annotations

from ..abstract.lang import BlockInfo
from ..core.value import get_symbolite_info
from ..ops._get_name import get_name
from ..ops.base import free_value


def validate_block_dependencies(info: BlockInfo) -> None:
    defined = {get_name(var) for var in info.inputs}

    for line_number, assignment in enumerate(info.lines, start=1):
        ainfo = get_symbolite_info(assignment)
        for var in free_value(ainfo.rhs):
            name = get_name(var)
            if name not in defined:
                raise ValueError(
                    f"Block line {line_number}: value '{name}' must be provided as an input or defined in a previous line."
                )

        defined.add(get_name(ainfo.lhs))

    for output in info.outputs:
        name = get_name(output)
        if name not in defined:
            raise ValueError(
                f"Block output value '{name}' must be provided as an input or defined in the block body."
            )


__all__ = [
    "validate_block_dependencies",
]
