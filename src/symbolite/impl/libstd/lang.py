"""
symbolite.impl.libstd.lang
~~~~~~~~~~~~~~~~~~~~~~~~~~

Standard-library implementations for language primitives.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import types
from typing import Any

import symbolite.impl.libpythoncode as libpythoncode
from symbolite.core import Unsupported

from ...abstract.lang import AssignInfo, BlockInfo
from ...ops._get_name import get_name
from ...ops._translate import translate
from .._lang_value_utils import compile as compile_code

CODE_IMPL = libpythoncode


def Assign(info: AssignInfo, *, libsl: Any) -> Any:
    """Translate AssignInfo into an executable assignment for the target backend."""
    compile_code(translate(info, CODE_IMPL))


def Block(info: BlockInfo, *, libsl: Any) -> Any:
    """Translate a BlockInfo into a callable that executes on the target backend."""
    source = translate(info, CODE_IMPL)
    namespace = compile_code(source, libsl=libsl)
    function = namespace[get_name(info)]
    function.__symbolite_def__ = source
    function.__symbolite_block__ = info
    return function


@translate.register(BlockInfo)
def translate_block_info(obj: BlockInfo, libsl: types.ModuleType) -> Any:
    lang_module = getattr(libsl, "lang", None)
    if lang_module is None or not hasattr(lang_module, "Block"):
        raise Unsupported(
            f"Implementation module {libsl.__name__} does not provide lang.Block translation."
        )
    translate_block = getattr(lang_module, "Block")
    return translate_block(obj, libsl=libsl)


@translate.register(AssignInfo)
def translate_assign_info(obj: AssignInfo, libsl: types.ModuleType) -> Any:
    lang_module = getattr(libsl, "lang", None)
    if lang_module is None or not hasattr(lang_module, "Assign"):
        raise Unsupported(
            f"Implementation module {libsl.__name__} does not provide lang.Assign translation."
        )
    translate_assign = getattr(lang_module, "Assign")
    return translate_assign(obj, libsl=libsl)


def _noop(value: Any, libsl: Any):
    return value


to_bool = _noop
to_int = _noop
to_float = _noop
to_tuple = _noop


def to_list(value: tuple[Any, ...], libsl: Any) -> list[Any]:
    return list(value)


def to_dict(value: tuple[tuple[Any, Any], ...], libsl: Any) -> dict[Any, Any]:
    items = to_tuple(value, libsl)
    return dict(items)


__all__ = [
    "CODE_IMPL",
    "Block",
    "Assign",
    "to_bool",
    "to_int",
    "to_float",
    "to_tuple",
    "to_list",
    "to_dict",
]
