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

from symbolite.abstract.boolean import Boolean
from symbolite.core.expression import NamedExpression

from ..abstract import Real, Symbol, Vector
from ..core import (
    Expression,
    Function,
    Named,
    SymbolicNamespace,
    SymbolicNamespaceMeta,
)


@singledispatch
def yield_named(
    self: Any, include_anonymous: bool = False
) -> Generator[Named, None, None]:
    """Yields all named structures inside a symbolic structure."""
    return
    yield Named()  # This is required to make it a generator.


@yield_named.register(tuple)
@yield_named.register(list)
def yield_named_tuple(expr: tuple[Any]) -> Generator[Named, None, None]:
    for el in expr:
        yield from yield_named(el)


@yield_named.register
def yield_named_named(
    self: Named, include_anonymous: bool = False
) -> Generator[Named, None, None]:
    if include_anonymous or self.name is not None:
        yield self


@yield_named.register
def yield_named_symbol_like(
    self: Symbol | Real | Vector | Boolean, include_anonymous: bool = False
) -> Generator[Named, None, None]:
    if self.expression is None:
        if include_anonymous or self.name is not None:
            yield self
    else:
        yield from yield_named(self.expression, include_anonymous)


@yield_named.register
def yield_named_base_function(
    self: Function, include_anonymous: bool = False
) -> Generator[Named, None, None]:
    yield self


@yield_named.register
def yield_named_expression(
    self: Expression, include_anonymous: bool = False
) -> Generator[Named, None, None]:
    if include_anonymous or self.func.name is not None:
        yield self.func

    for arg in self.args:
        yield from yield_named(arg, include_anonymous)

    for _, v in self.kwargs_items:
        yield from yield_named(v, include_anonymous)


@yield_named.register
def yield_named_named_expression(
    self: NamedExpression, include_anonymous: bool = False
) -> Generator[Named, None, None]:
    yield from yield_named_named(self, include_anonymous)
    yield from yield_named(self.expression, include_anonymous)


@yield_named.register
def _(
    self: SymbolicNamespaceMeta | SymbolicNamespace, include_anonymous: bool = False
) -> Generator[Named, None, None]:
    assert isinstance(self, (SymbolicNamespace, SymbolicNamespaceMeta))
    for name in dir(self):
        if name.startswith("__"):
            continue
        attr = getattr(self, name)
        yield from yield_named(attr, include_anonymous)
