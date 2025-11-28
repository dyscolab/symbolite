"""
symbolite.impl.libsympy.lang
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SymPy-backed implementations for language primitives.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import types
from typing import Any

import sympy
from sympy import Symbol
from sympy.codegen.ast import (
    Assignment,
    CodeBlock,
    FunctionDefinition,
    Return,
    real,
)

from ...abstract.lang import AssignInfo, BlockInfo
from ...ops import get_name, translate


def Assign(info: AssignInfo, libsl: types.ModuleType) -> Assignment:
    """Translate an AssignInfo into a Python assignment statement."""
    return Assignment(Symbol(get_name(info.lhs)), translate(info.rhs, libsl))


def Block(info: BlockInfo, libsl: types.ModuleType):
    """Translate a BlockInfo into a Python function definition."""

    parameters = tuple(Symbol(get_name(var), real=True) for var in info.inputs)

    outputs = tuple(Symbol(get_name(var), real=True) for var in info.outputs)

    if len(outputs) == 0:
        ret = Return()
    elif len(outputs) == 1:
        ret = Return(outputs[0])
    else:
        ret = Return(sympy.Tuple(*outputs))

    return FunctionDefinition(
        return_type=real,
        name=get_name(info),
        parameters=parameters,
        body=CodeBlock(
            *(translate(assign, libsl) for assign in info.lines),
            ret,
        ),
    )


def _return(value: Any, libsl: Any):
    return value


to_bool = _return
to_int = _return
to_float = _return


def to_tuple(value: tuple[Any, ...]):
    return sympy.Tuple(value)


def to_list(value: tuple[Any, ...], libsl: Any) -> list[Any]:
    return list(value)


def to_dict(value: tuple[tuple[Any, Any], ...], libsl: Any) -> dict[Any, Any]:
    items = to_tuple(value, libsl)
    return dict(items)
