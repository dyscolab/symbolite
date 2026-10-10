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
from sympy.codegen.ast import (
    Assignment,
    CodeBlock,
    FunctionDefinition,
    Return,
    Variable,
    untyped,
)

from ...core.lang import Assign as _Assign
from ...core.lang import Block as _Block
from ...core.symbolite_object import get_symbolite_info
from ...ops import get_name, translate


def _parameter(value: Any, libsl: types.ModuleType) -> Variable:
    symbol = translate(value, libsl)
    try:
        return Variable.deduced(symbol)
    except ValueError:
        # Generic symbols have no numeric type assumptions to infer from.
        return Variable(symbol, type=untyped)


def Assign(obj: _Assign, libsl: types.ModuleType) -> Assignment:
    """Translate a symbolic assignment into a SymPy assignment node."""
    info = get_symbolite_info(obj)
    return Assignment(translate(info.lhs, libsl), translate(info.rhs, libsl))


def Block(obj: _Block, libsl: types.ModuleType) -> FunctionDefinition:
    """Translate a symbolic Block into a SymPy function-definition AST."""
    info = get_symbolite_info(obj)

    parameters = tuple(_parameter(var, libsl) for var in info.inputs)

    outputs = tuple(translate(var, libsl) for var in info.outputs)

    if len(outputs) == 0:
        ret = Return(None)
    elif len(outputs) == 1:
        ret = Return(outputs[0])
    else:
        ret = Return(sympy.Tuple(*outputs))

    return FunctionDefinition(
        return_type=untyped,
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


def to_tuple(value: tuple[Any, ...], libsl: Any) -> sympy.Tuple:
    # Children are already translated by the structural fold.
    return sympy.Tuple(*value)


def to_list(value: tuple[Any, ...], libsl: Any) -> list[Any]:
    return list(value)


def to_dict(value: tuple[tuple[Any, Any], ...], libsl: Any) -> dict[Any, Any]:
    return dict(value)
