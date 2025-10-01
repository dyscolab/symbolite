"""
symbolite.core.expression
~~~~~~~~~~~~~~~~~~~~~~~~~

An expression is the result of a function that has been called with
certain arguments.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
import functools
from typing import TYPE_CHECKING, Any, Self

from .named import Named

if TYPE_CHECKING:
    from .function import Function


@dataclasses.dataclass(frozen=True, repr=False)
class Expression[T_co: "NamedExpression"]:
    """A Function that has been called with certain arguments."""

    func: Function[T_co]
    args: tuple[Any, ...]
    kwargs_items: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.kwargs_items, dict):
            object.__setattr__(self, "kwargs_items", tuple(self.kwargs_items.items()))

    @functools.cached_property
    def kwargs(self) -> dict[str, Any]:
        return dict(self.kwargs_items)

    def __repr__(self) -> str:
        from ..ops.util import repr_without_defaults

        return repr_without_defaults(self)

    def __str__(self) -> str:
        from ..ops import as_string

        return as_string(self)


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class NamedExpression(Named):
    """An expression with name and namespace."""

    expression: Expression[Self] | None = None
