"""
symbolite.core.ops.substitute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace symbols, functions, values, etc by others.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import inspect
from collections.abc import Mapping
from functools import singledispatch
from typing import Any

from ..core import Call, SymbolicNamespace, SymbolicNamespaceMeta
from ..core.symbolite_object import get_symbolite_info
from ..core.variable import Name, Variable


@singledispatch
def substitute(obj: Any, replacements: Mapping[Any, Any]) -> Any:
    """Replace symbols, functions, values, etc by others.

    Parameters
    ----------
    obj
        symbolic expression.
    replacements
        replacement dictionary.
    """
    return replacements.get(obj, obj)


@substitute.register(Variable)
def substitute_variable[R: Variable[Any]](obj: R, mapper: Mapping[Any, Any]) -> R:
    info = get_symbolite_info(obj)
    if isinstance(info.value, Name):
        return mapper.get(obj, obj)
    return obj.__class__(substitute(info.value, mapper))


@substitute.register
def substitue_call(obj: Call, mapper: Mapping[Any, Any]) -> Call:
    info = get_symbolite_info(obj)
    func = mapper.get(info.func, info.func)
    args = tuple(substitute(arg, mapper) for arg in info.args)
    kwargs = {k: substitute(arg, mapper) for k, arg in info.kwargs_items}

    return Call(func, args, tuple(kwargs.items()))


@substitute.register(SymbolicNamespaceMeta)
@substitute.register(SymbolicNamespace)
def _(
    obj: SymbolicNamespace | SymbolicNamespaceMeta, replacements: Mapping[Any, Any]
) -> Any:
    assert isinstance(obj, (SymbolicNamespace, SymbolicNamespaceMeta))

    d = {}
    for attr_name in dir(obj):
        if attr_name.startswith("__"):
            continue
        attr = getattr(obj, attr_name)
        d[attr_name] = substitute(attr, replacements)

    return type(obj.__name__, inspect.getmro(obj), d)
