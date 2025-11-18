"""
symbolite.ops._translate
~~~~~~~~~~~~~~~~~~~~~~~~

Translate a symbolic structure using an implementation.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from functools import singledispatch
from operator import attrgetter
from typing import Any

from ..core import (
    Unsupported,
)
from ..core.call import CallInfo
from ..core.function import FunctionInfo, OperatorInfo, UserFunctionInfo
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.value import Name, Value
from ._get_name import get_name


@singledispatch
def translate(obj: Any, libsl: types.ModuleType) -> Any:
    """Translate expression into backend representation.

    Parameters
    ----------
    obj
        symbolic expression.
    libsl
        implementation module.
    """
    return obj


@translate.register
def translate_bool(obj: bool, libsl: types.ModuleType) -> Any:
    return libsl.lang.to_bool(obj, libsl)


@translate.register
def translate_builtin_int(obj: int, libsl: types.ModuleType) -> Any:
    return libsl.lang.to_int(obj, libsl)


@translate.register
def translate_builtin_float(obj: float, libsl: types.ModuleType) -> Any:
    return libsl.lang.to_float(obj, libsl)


@translate.register(tuple)
def translate_tuple(obj: tuple[Any, ...], libsl: types.ModuleType) -> Any:
    return libsl.lang.to_tuple(tuple(translate(value, libsl) for value in obj), libsl)


@translate.register(list)
def translate_list(obj: list[Any], libsl: types.ModuleType) -> Any:
    return libsl.lang.to_list(tuple(translate(value, libsl) for value in obj), libsl)


@translate.register(dict)
def translate_dict(obj: dict[Any, Any], libsl: types.ModuleType) -> Any:
    return libsl.lang.to_dict(
        tuple(
            (translate(key, libsl), translate(value, libsl))
            for key, value in obj.items()
        ),
        libsl,
    )


@translate.register
def translate_str(obj: str, libsl: types.ModuleType) -> Any:  # | Unsupported:
    # TODO: Remove?
    return attrgetter(obj)(libsl)


@translate.register(SymboliteObject)
def translate_symbolite_object(
    obj: SymboliteObject[Any], libsl: types.ModuleType
) -> Any:
    info = get_symbolite_info(obj)
    return translate(info, libsl)


@translate.register(Value)
def translate_value(obj: Value[Any], libsl: types.ModuleType) -> Any:
    info = get_symbolite_info(obj)
    if not isinstance(info.value, Name):
        return translate(info.value, libsl)

    symbol_name, namespace = info.value.name, info.value.namespace

    if namespace:
        name = get_name(obj, qualified=True)
        value = translate(name, libsl)

        if value is Unsupported:
            raise Unsupported(f"{name} is not supported in module {libsl.__name__}")

        return value

    # User defined symbol, try to map the class
    name = f"{obj.__class__.__module__.split('.')[-1]}.{obj.__class__.__name__}"
    f = translate(name, libsl)

    if f is Unsupported:
        raise Unsupported(f"{name} is not supported in module {libsl.__name__}")

    return f(symbol_name)


@translate.register(FunctionInfo)
def translate_function_info(
    obj: FunctionInfo[Any], libsl: types.ModuleType
) -> Any | Unsupported:
    attr_name = f"{obj.namespace}.{obj.name}"
    return attrgetter(attr_name)(libsl)


@translate.register(OperatorInfo)
def translate_operator_info(
    obj: OperatorInfo[Any], libsl: types.ModuleType
) -> Any | Unsupported:
    attr_name = f"{obj.namespace}.{obj.name}"
    return attrgetter(attr_name)(libsl)


@translate.register(CallInfo)
def translate_call_info(obj: CallInfo, libsl: types.ModuleType) -> Any:
    func = translate(obj.func, libsl)
    args = tuple(translate(arg, libsl) for arg in obj.args)
    kwargs = {k: translate(arg, libsl) for k, arg in obj.kwargs_items}

    try:
        return func(*args, **kwargs)
    except Exception as ex:
        try:
            ex.add_note(f"While translating {func}(*{args}, **{kwargs}): {ex}")
        except AttributeError:
            pass
        raise ex


@translate.register(UserFunctionInfo)
def translate_user_function_info(
    obj: UserFunctionInfo[Any, Any, Any], libsl: types.ModuleType
) -> Any:
    impls = obj.impls
    default = None
    for k, v in impls:
        if k is libsl:
            return v
        elif k == "default":
            default = v
    if default is not None:
        return default

    raise Exception(
        f"No implementation found for {libsl.__name__} and no default implementation provided for function {obj!s}"
    )
