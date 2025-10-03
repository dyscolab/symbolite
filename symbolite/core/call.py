"""
symbolite.core.expression
~~~~~~~~~~~~~~~~~~~~~~~~~

An expression is the result of a function that has been called with
certain arguments.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

from .symbolite_object import SymboliteObject, set_symbolite_info

if TYPE_CHECKING:
    from .function import SymbolicCallable


class CallInfo(NamedTuple):
    func: SymbolicCallable[Any]
    args: tuple[Any, ...]
    kwargs_items: tuple[tuple[str, Any], ...]


class Call(SymboliteObject[CallInfo]):
    """A Function that has been called with certain arguments."""

    def __init__(
        self,
        func: SymbolicCallable[Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any] | tuple[tuple[str, Any], ...],
    ) -> None:
        if isinstance(kwargs, dict):
            kwargs = tuple(kwargs.items())

        set_symbolite_info(self, CallInfo(func, args, kwargs))
