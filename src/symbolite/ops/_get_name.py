"""
symbolite.ops._get_name
~~~~~~~~~~~~~~~~~~~~~~~

Utilities to retrieve symbolic names in a consistent way.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from functools import singledispatch
from typing import Any

from ..core.function import FunctionInfo, OperatorInfo, UserFunctionInfo
from ..core.lang import BlockInfo
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.value import Name, ValueInfo

#################
# get_full_name
#################


@singledispatch
def get_full_name(obj: Name) -> str:
    if obj.namespace:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@get_full_name.register(ValueInfo)
def get_full_name_value(obj: ValueInfo[Any]) -> str:
    if isinstance(obj.value, Name):
        return get_full_name(obj.value)
    else:
        return "<anonymous>"


@get_full_name.register(SymboliteObject)
def get_full_name_symbolite_object(obj: SymboliteObject[Any]) -> str:
    info = get_symbolite_info(obj)
    return get_full_name(info)


#################
# get_name
#################


@singledispatch
def get_name(obj: Name) -> str:
    return obj.name


@get_name.register(SymboliteObject)
def get_name_symbolite_object(obj: SymboliteObject[Any]) -> str:
    info = get_symbolite_info(obj)
    return get_name(info)


@get_name.register(ValueInfo)
def get_name_value(obj: ValueInfo[Any]) -> str:
    if isinstance(obj.value, Name):
        return get_name(obj.value)
    else:
        return "<anonymous>"


@get_name.register(FunctionInfo)
def get_name_function(obj: FunctionInfo[Any]) -> str:
    if obj.namespace:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@get_name.register(OperatorInfo)
def get_name_operator(obj: OperatorInfo[Any]) -> str:
    if obj.namespace:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@get_name.register(UserFunctionInfo)
def get_name_user_function_info(obj: UserFunctionInfo[Any, Any, Any]) -> str:
    if obj.namespace:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@get_name.register
def get_name_block_info(obj: BlockInfo) -> str:
    return obj.name or "__symbolite_block"


#################
# get_namespace
#################


@singledispatch
def get_namespace(obj: Any) -> str | None:
    return None


@get_namespace.register(SymboliteObject)
def get_namespace_symbolite_object(obj: SymboliteObject[Any]) -> str | None:
    info = get_symbolite_info(obj)
    return get_namespace(info)


@get_namespace.register(ValueInfo)
def get_namespace_value(obj: ValueInfo[Any]) -> str | None:
    if isinstance(obj.value, Name):
        return obj.value.namespace
    return None


@get_namespace.register(FunctionInfo)
def get_namespace_function(obj: FunctionInfo[Any]) -> str | None:
    return obj.namespace


@get_namespace.register(OperatorInfo)
def get_namespace_operator(obj: OperatorInfo[Any]) -> str | None:
    return obj.namespace


@get_namespace.register(UserFunctionInfo)
def get_namespace_user_function(obj: UserFunctionInfo[Any, Any, Any]) -> str | None:
    return obj.namespace
