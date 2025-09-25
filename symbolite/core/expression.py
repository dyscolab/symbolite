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
from typing import Any

from .named import Named


@dataclasses.dataclass(frozen=True, repr=False)
class Expression:
    """A Function that has been called with certain arguments."""

    func: Named
    args: tuple[Any, ...]
    kwargs_items: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.kwargs_items, dict):
            object.__setattr__(self, "kwargs_items", tuple(self.kwargs_items.items()))

    @functools.cached_property
    def kwargs(self) -> dict[str, Any]:
        return dict(self.kwargs_items)

    def __str__(self) -> str:
        return self.func.format(*self.args, *self.kwargs)

    def __repr__(self) -> str:
        from ..ops.util import repr_without_defaults
        return repr_without_defaults(self)


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class NamedExpression(Named):
    """An expression with name and namespace."""

    expression: Expression | None = None
