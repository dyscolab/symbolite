"""Utilities to retrieve symbolic names in a consistent way."""

from __future__ import annotations

from functools import singledispatch
from typing import Any

from ..core.function import FunctionInfo, OperatorInfo, UserFunctionInfo
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.value import Name, ValueInfo


@singledispatch
def get_name(obj: Name, qualified: bool = True) -> str:
    if obj.namespace and qualified:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@get_name.register(SymboliteObject)
def get_name_symbolite_object(obj: SymboliteObject[Any], qualified: bool = True) -> str:
    info = get_symbolite_info(obj)
    return get_name(info, qualified=qualified)


@get_name.register(ValueInfo)
def get_name_value(obj: ValueInfo[Any], qualified: bool = True) -> str:
    if isinstance(obj.value, Name):
        return get_name(obj.value, qualified=qualified)
    else:
        return "<anonymous>"


@get_name.register(FunctionInfo)
def get_name_function(obj: FunctionInfo[Any], qualified: bool = True) -> str:
    if obj.namespace and qualified:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@get_name.register(OperatorInfo)
def get_name_operator(obj: OperatorInfo[Any], qualified: bool = True) -> str:
    if obj.namespace and qualified:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


@get_name.register(UserFunctionInfo)
def get_name_user_function_info(
    obj: UserFunctionInfo[Any, Any, Any], qualified: bool = True
) -> str:
    if obj.namespace and qualified:
        return f"{obj.namespace}.{obj.name}"
    return obj.name


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
