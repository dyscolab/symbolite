"""
symbolite.impl.libpythoncode.lang
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code-emitting counterparts for language primitives.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from typing import Any

from typing_extensions import type_repr

import symbolite.impl.libpythoncode as libpythoncode

from ...abstract.lang import AssignInfo, BlockInfo
from ...ops._get_name import get_name
from ...ops._translate import translate


def Block(info: BlockInfo, **_: Any) -> str:
    """Translate a BlockInfo into a Python function definition."""

    parameters = tuple(
        f"{get_name(var, qualified=False)}: {type_repr(var.__class__).removeprefix('symbolite.abstract.')}"
        for var in info.inputs
    )
    body = [translate(assign, libpythoncode) for assign in info.lines]

    ret = {
        f"{get_name(var)}": f"{type_repr(var.__class__).removeprefix('symbolite.abstract.')}"
        for var in info.outputs
    }

    match len(info.outputs):
        case 0:
            return_vars, return_ann = "None", "None"
        case 1:
            return_vars, return_ann = ret.popitem()
        case _:
            # Note: this assumes iter keys an values separately preserves order
            return_vars = ", ".join(ret.keys())
            return_ann = "tuple[" + ", ".join(ret.values()) + "]"

    header = f"def {get_name(info, qualified=False)}({', '.join(parameters)}) -> {return_ann}"

    parts = [f"{header}:"]
    if body:
        parts.append("    " + "\n    ".join(body))
    parts.append(f"    return {return_vars}")

    return "\n".join(parts)


def Assign(info: AssignInfo, **_: Any) -> str:
    """Translate an AssignInfo into a Python assignment statement."""

    lhs = get_name(info.lhs, qualified=False)
    rhs = translate(info.rhs, libpythoncode)
    return f"{lhs} = {rhs}"


def to_bool(value: bool, libsl: Any) -> str:
    return "True" if value else "False"


def to_int(value: int, libsl: Any) -> str:
    return repr(value)


def to_float(value: float, libsl: Any) -> str:
    return repr(value)


def to_tuple(value: tuple[Any, ...], libsl: Any) -> str:
    value = (str(v) for v in value)
    return f"({', '.join(value)}, )"


def to_list(value: tuple[Any, ...], libsl: Any) -> str:
    value = (str(v) for v in value)
    return f"[{', '.join(value)}]"


def to_dict(value: tuple[tuple[Any, Any], ...], libsl: Any) -> str:
    items = to_tuple(value, libsl)
    return f"dict({items})"


__all__ = [
    "Block",
    "Assign",
    "to_bool",
    "to_int",
    "to_float",
    "to_tuple",
    "to_list",
    "to_dict",
]
