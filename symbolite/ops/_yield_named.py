"""
symbolite.core.ops.yield_named
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from collections.abc import Generator
from functools import singledispatch
from typing import Any

from ..core import (
    Call,
    Function,
    SymbolicNamespace,
    SymbolicNamespaceMeta,
    Variable,
)
from ..core.function import Operator, UserFunction
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.variable import Name


@singledispatch
def yield_named(obj: Any) -> Generator[SymboliteObject[Any], None, None]:
    """Yields all named structures inside a symbolic structure."""
    return
    yield SymboliteObject()  # This is required to make it a generator.


@yield_named.register(tuple)
@yield_named.register(list)
def yield_named_tuple(obj: tuple[Any]) -> Generator[SymboliteObject[Any], None, None]:
    for el in obj:
        yield from yield_named(el)


@yield_named.register(SymboliteObject)
def yield_named_symbolite_object(
    obj: SymboliteObject[Any],
) -> Generator[SymboliteObject[Any], None, None]:
    info = get_symbolite_info(obj)
    yield from yield_named(info)


@yield_named.register(Variable)
def yield_named_variable(
    obj: Variable[Any],
) -> Generator[SymboliteObject[Any], None, None]:
    info = get_symbolite_info(obj)
    if isinstance(info.value, Name):
        yield obj
    else:
        yield from yield_named(info.value)


@yield_named.register(Function | Operator | UserFunction)
def yield_named_base_function(
    obj: Function[Any] | Operator[Any] | UserFunction[Any, Any, Any],
) -> Generator[SymboliteObject[Any], None, None]:
    yield obj


@yield_named.register
def yield_named_call(obj: Call) -> Generator[SymboliteObject[Any], None, None]:
    info = get_symbolite_info(obj)
    yield from yield_named(info.func)
    for arg in info.args:
        yield from yield_named(arg)

    for _, v in info.kwargs_items:
        yield from yield_named(v)


@yield_named.register
def _(
    obj: SymbolicNamespaceMeta | SymbolicNamespace,
) -> Generator[SymboliteObject[Any], None, None]:
    assert isinstance(obj, (SymbolicNamespace, SymbolicNamespaceMeta))
    for name in dir(obj):
        if name.startswith("__"):
            continue
        attr = getattr(obj, name)
        if isinstance(attr, SymboliteObject):
            yield from yield_named(attr)
