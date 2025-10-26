"""
symbolite.ops._translate_impl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from functools import singledispatch
from operator import attrgetter
from typing import Any

from ..core import (
    SymbolicNamespace,
    SymbolicNamespaceMeta,
    Unsupported,
)
from ..core.call import CallInfo
from ..core.function import FunctionInfo, OperatorInfo, UserFunction
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.variable import Name, Variable
from ._get_name import get_name


@singledispatch
def translate_impl(obj: Any, libsl: types.ModuleType) -> Any:
    """Translate expression into backend representation.

    Parameters
    ----------
    obj
        symbolic expression.
    libsl
        implementation module.
    """
    return obj


@translate_impl.register
def translate_impl_str(obj: str, libsl: types.ModuleType) -> Any:  # | Unsupported:
    return attrgetter(obj)(libsl)


@translate_impl.register(SymboliteObject)
def translate_impl_symbolite_object(
    obj: SymboliteObject[Any], libsl: types.ModuleType
) -> Any:
    info = get_symbolite_info(obj)
    return translate_impl(info, libsl)


@translate_impl.register(Variable)
def translate_variable(obj: Variable[Any], libsl: types.ModuleType) -> Any:
    info = get_symbolite_info(obj)
    if not isinstance(info.value, Name):
        return translate_impl(info.value, libsl)

    symbol_name, namespace = info.value.name, info.value.namespace

    if namespace:
        name = get_name(obj, qualified=True)
        value = translate_impl(name, libsl)

        if value is Unsupported:
            raise Unsupported(f"{name} is not supported in module {libsl.__name__}")

        return value

    # User defined symbol, try to map the class
    name = f"{obj.__class__.__module__.split('.')[-1]}.{obj.__class__.__name__}"
    f = translate_impl(name, libsl)

    if f is Unsupported:
        raise Unsupported(f"{name} is not supported in module {libsl.__name__}")

    return f(symbol_name)


@translate_impl.register(FunctionInfo)
def _(obj: FunctionInfo[Any], libsl: types.ModuleType) -> Any | Unsupported:
    attr_name = f"{obj.namespace}.{obj.name}"
    return attrgetter(attr_name)(libsl)


@translate_impl.register(OperatorInfo)
def _(obj: OperatorInfo[Any], libsl: types.ModuleType) -> Any | Unsupported:
    attr_name = f"{obj.namespace}.{obj.name}"
    return attrgetter(attr_name)(libsl)


@translate_impl.register(SymbolicNamespaceMeta)
@translate_impl.register(SymbolicNamespace)
def _(obj: SymbolicNamespace | SymbolicNamespaceMeta, libsl: types.ModuleType) -> Any:
    assert isinstance(obj, (SymbolicNamespace, SymbolicNamespaceMeta))
    return {
        attr_name: translate_impl(getattr(obj, attr_name), libsl)
        for attr_name in dir(obj)
        if not attr_name.startswith("__")
    }


@translate_impl.register(CallInfo)
def _(obj: CallInfo, libsl: types.ModuleType) -> Any:
    func = translate_impl(obj.func, libsl)
    args = tuple(translate_impl(arg, libsl) for arg in obj.args)
    kwargs = {k: translate_impl(arg, libsl) for k, arg in obj.kwargs_items}

    try:
        return func(*args, **kwargs)
    except Exception as ex:
        try:
            ex.add_note(f"While translating {func}(*{args}, **{kwargs}): {ex}")
        except AttributeError:
            pass
        raise ex


@translate_impl.register(UserFunction)
def _(obj: UserFunction[Any, Any, Any], libsl: types.ModuleType) -> Any:
    impls = obj._impls
    if libsl in impls:
        return impls[libsl]
    elif "default" in impls:
        return impls["default"]
    else:
        raise Exception(
            f"No implementation found for {libsl.__name__} and no default implementation provided for function {obj!s}"
        )
