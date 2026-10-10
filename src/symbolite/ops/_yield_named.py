"""Named-object discovery over the shared structural traversal."""

from collections.abc import Generator
from functools import singledispatch
from typing import Any

from ..core.call import Call
from ..core.function import Function, Operator, UserFunction
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.value import Name, Value
from ._dispatch import TraversalDispatch


@singledispatch
def yield_named(obj: Any) -> Generator[SymboliteObject[Any], None, None]:
    """Yield named values/functions in preorder, once per occurrence.

    Registered operation handlers override structural adapters at any depth.
    Dictionary keys and values are inspected in insertion order.
    """

    for node, selected in _dispatch.walk(obj):
        if selected is not None:
            yield from _dispatch.iterate(node, selected)
        elif isinstance(node, (Function, Operator, UserFunction)) or (
            isinstance(node, Value) and isinstance(get_symbolite_info(node).value, Name)
        ):
            yield node


_dispatch = TraversalDispatch(
    yield_named, metadata_exclusions=(Value, Call, Function, Operator, UserFunction)
)
