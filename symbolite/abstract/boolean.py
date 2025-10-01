"""
symbolite.abstract.symbol
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for symbol operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
from typing import Self

from ..core import NamedExpression
from ..core.function import BinaryOperator


@dataclasses.dataclass(frozen=True, repr=False)
class Boolean(NamedExpression):
    """Boolean symbolic expression."""

    def __and__(self, other: Self) -> Boolean:
        """Implements bitwise and using the & operator."""
        return and_(self, other)

    def __or__(self, other: Self) -> Boolean:
        """Implements bitwise or using the | operator."""
        return or_(self, other)

    def __xor__(self, other: Self) -> Boolean:
        """Implements bitwise xor using the ^ operator."""
        return xor(self, other)

    def __rand__(self, other: Self) -> Boolean:
        """Implements reflected bitwise and using the & operator."""
        return and_(other, self)

    def __ror__(self, other: Self) -> Boolean:
        """Implements reflected bitwise or using the | operator."""
        return or_(other, self)

    def __rxor__(self, other: Self) -> Boolean:
        """Implements reflected bitwise xor using the ^ operator."""
        return xor(other, self)


BinOp = BinaryOperator[Boolean, Boolean]

and_ = BinOp("and_", "boolean", precedence=-2, fmt="{} & {}", result_cls=Boolean)
xor = BinOp("xor", "boolean", precedence=-3, fmt="{} ^ {}", result_cls=Boolean)
or_ = BinOp("or_", "boolean", precedence=-4, fmt="{} | {}", result_cls=Boolean)
