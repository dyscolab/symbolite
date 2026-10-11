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

from ...abstract.lang import Assign as _Assign
from ...abstract.lang import Block as _Block
from ...core.symbolite_object import get_symbolite_info
from ...core.value import Name
from ...ops._get_name import get_full_name, get_name
from ...ops._translate import translate
from ._codeexpr import CodeExpr, _coerce, validate_identifier, validate_qualified_name


def Block(obj: _Block, libsl: Any) -> str:
    """Translate a BlockInfo into a Python function definition."""

    info = get_symbolite_info(obj)
    name = validate_identifier(get_name(info), role="block name")

    input_names = []
    for var in info.inputs:
        value = get_symbolite_info(var).value
        if not isinstance(value, Name) or value.namespace:
            raise ValueError("Python block inputs must be unqualified named values.")
        input_names.append(validate_identifier(value.name, role="parameter name"))
    if len(set(input_names)) != len(input_names):
        raise ValueError("Python block input names must be unique.")

    parameters = tuple(
        f"{name}: {type_repr(var.__class__).removeprefix('symbolite.abstract.')}"
        for name, var in zip(input_names, info.inputs)
    )

    body = [translate(assign, libsl) for assign in info.lines]

    ret = tuple(
        (
            validate_qualified_name(get_full_name(var)),
            type_repr(var.__class__).removeprefix("symbolite.abstract."),
        )
        for var in info.outputs
    )

    match len(info.outputs):
        case 0:
            return_vars, return_ann = "None", "None"
        case 1:
            (return_vars, return_ann) = ret[0]
        case _:
            return_vars = ", ".join(name for name, _ in ret)
            return_ann = "tuple[" + ", ".join(annotation for _, annotation in ret) + "]"

    header = f"def {name}({', '.join(parameters)}) -> {return_ann}"

    parts = [f"{header}:"]
    if body:
        parts.append("    " + "\n    ".join(body))
    parts.append(f"    return {return_vars}")

    return "\n".join(parts)


def Assign(obj: _Assign, libsl: Any) -> str:
    """Translate an AssignInfo into a Python assignment statement."""

    info = get_symbolite_info(obj)

    lhs = translate(info.lhs, libsl)
    rhs = translate(info.rhs, libsl)
    return f"{lhs!s} = {rhs!s}"


def to_bool(value: bool, libsl: Any) -> str:
    return "True" if value else "False"


def to_int(value: int, libsl: Any) -> CodeExpr:
    return _coerce(value)


def to_float(value: float, libsl: Any) -> CodeExpr:
    return _coerce(value)


def to_str(value: str, libsl: Any) -> CodeExpr:
    return CodeExpr(repr(value))


def to_tuple(value: tuple[Any, ...], libsl: Any) -> str:
    # Children have already been translated by the structural fold.
    if not value:
        return "()"
    return f"({', '.join(map(str, value))}, )"


def to_list(value: tuple[Any, ...], libsl: Any) -> str:
    return f"[{', '.join(map(str, value))}]"


def to_dict(value: tuple[tuple[Any, Any], ...], libsl: Any) -> str:
    items = (f"({key}, {item})" for key, item in value)
    return f"dict([{', '.join(items)}])"


__all__ = [
    "Assign",
    "Block",
    "to_bool",
    "to_dict",
    "to_float",
    "to_int",
    "to_list",
    "to_str",
    "to_tuple",
]
