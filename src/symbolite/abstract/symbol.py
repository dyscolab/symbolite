"""
symbolite.abstract.symbol
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for symbol operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from typing import Any

from ..core import Value
from ..core.function import (
    BinaryOperator,
    Function3,
    UnaryOperator,
)
from .boolean import Boolean


class Symbol(Value[Any]):
    """General purpose symbolic value.

    The following magic methods are not mapped to symbolite Functions
      - __hash__, __eq__, __ne__ collides with reasonble use of comparisons
        within user code (including uses as dict keys).
        We defined `.eq` y `.ne` methods for the two lasts.
      - __contains__ is coerced to boolean.
      - __bool__ yields a TypeError if not boolean.
      - __str__, __bytes__, __repr__ yields a TypeError if the return value
        is not of the corresponding type.
        and they might also affect usability in the console.
      - __format__
      - __int__, __float__, __complex__ yields a TypeError if the return value
        is not of the corresponding type.
      - __round__, __abs__, __divmod__ they are too "numeric related"
      - __trunc__, __ceil__, __floor__ they are too "numeric related"
        and called by functions in math.
      - __len__ yields a TypeError if not int.
      - __index__ yields a TypeError if not int.

    Also, magic methods that are statements (not expressions) are also not
    mapped: e.g. __setitem__ or __delitem__

    See Value for more information.
    """

    # Comparison methods (not operator)
    def eq(self, other: Any) -> Boolean:
        return eq(self, other)

    def ne(self, other: Any) -> Boolean:
        return ne(self, other)

    # Comparison magic methods
    def __lt__(self, other: Any) -> Boolean:
        """Implements less than comparison using the < operator."""
        return lt(self, other)

    def __le__(self, other: Any) -> Boolean:
        """Implements less than or equal comparison using the <= operator."""
        return le(self, other)

    def __gt__(self, other: Any) -> Boolean:
        """Implements greater than comparison using the > operator."""
        return gt(self, other)

    def __ge__(self, other: Any) -> Boolean:
        """Implements greater than or equal comparison using the >= operator."""
        return ge(self, other)

    # Emulating container types
    def __getitem__(self, key: Any) -> Symbol:
        """Defines behavior for when an item is accessed,
        using the notation self[key]."""
        return getitem(self, key)

    # Emulating attribute
    def __getattr__(self, key: str) -> Symbol:
        """Defines behavior for when an item is accessed,
        using the notation self.key"""
        if key.startswith("__"):
            raise AttributeError(key)
        return symgetattr(self, key)

    # Normal arithmetic operators
    def __add__(self, other: Any) -> Symbol:
        """Implements addition."""
        return add(self, other)

    def __sub__(self, other: Any) -> Symbol:
        """Implements subtraction."""
        return sub(self, other)

    def __mul__(self, other: Any) -> Symbol:
        """Implements multiplication."""
        return mul(self, other)

    def __matmul__(self, other: Any) -> Symbol:
        """Implements multiplication."""
        return matmul(self, other)

    def __truediv__(self, other: Any) -> Symbol:
        """Implements true division."""
        return truediv(self, other)

    def __floordiv__(self, other: Any) -> Symbol:
        """Implements integer division using the // operator."""
        return floordiv(self, other)

    def __mod__(self, other: Any) -> Symbol:
        """Implements modulo using the % operator."""
        return mod(self, other)

    def __pow__(self, other: Any, modulo: Any = None) -> Symbol:
        """Implements behavior for exponents using the ** operator."""
        if modulo is None:
            return pow(self, other)
        else:
            return pow3(self, other, modulo)

    def __lshift__(self, other: Any) -> Symbol:
        """Implements left bitwise shift using the << operator."""
        return lshift(self, other)

    def __rshift__(self, other: Any) -> Symbol:
        """Implements right bitwise shift using the >> operator."""
        return rshift(self, other)

    def __and__(self, other: Any) -> Symbol:
        """Implements bitwise and using the & operator."""
        return and_(self, other)

    def __or__(self, other: Any) -> Symbol:
        """Implements bitwise or using the | operator."""
        return or_(self, other)

    def __xor__(self, other: Any) -> Symbol:
        """Implements bitwise xor using the ^ operator."""
        return xor(self, other)

    # Reflected arithmetic operators
    def __radd__(self, other: Any) -> Symbol:
        """Implements reflected addition."""
        return add(other, self)

    def __rsub__(self, other: Any) -> Symbol:
        """Implements reflected subtraction."""
        return sub(other, self)

    def __rmul__(self, other: Any) -> Symbol:
        """Implements reflected multiplication."""
        return mul(other, self)

    def __rmatmul__(self, other: Any) -> Symbol:
        """Implements reflected multiplication."""
        return matmul(other, self)

    def __rtruediv__(self, other: Any) -> Symbol:
        """Implements reflected true division."""
        return truediv(other, self)

    def __rfloordiv__(self, other: Any) -> Symbol:
        """Implements reflected integer division using the // operator."""
        return floordiv(other, self)

    def __rmod__(self, other: Any) -> Symbol:
        """Implements reflected modulo using the % operator."""
        return mod(other, self)

    def __rpow__(self, other: Any) -> Symbol:
        """Implements behavior for reflected exponents using the ** operator."""
        return pow(other, self)

    def __rlshift__(self, other: Any) -> Symbol:
        """Implements reflected left bitwise shift using the << operator."""
        return lshift(other, self)

    def __rrshift__(self, other: Any) -> Symbol:
        """Implements reflected right bitwise shift using the >> operator."""
        return rshift(other, self)

    def __rand__(self, other: Any) -> Symbol:
        """Implements reflected bitwise and using the & operator."""
        return and_(other, self)

    def __ror__(self, other: Any) -> Symbol:
        """Implements reflected bitwise or using the | operator."""
        return or_(other, self)

    def __rxor__(self, other: Any) -> Symbol:
        """Implements reflected bitwise xor using the ^ operator."""
        return xor(other, self)

    # Unary operators and functions
    def __neg__(self) -> Symbol:
        """Implements behavior for negation (e.g. -some_object)"""
        return neg(self)

    def __pos__(self) -> Symbol:
        """Implements behavior for unary positive (e.g. +some_object)"""
        return pos(self)

    def __invert__(self) -> Symbol:
        """Implements behavior for inversion using the ~ operator."""
        return invert(self)


CompOp = BinaryOperator[Any, Any, Boolean]
BinOp = BinaryOperator[Any, Any, Symbol]
BinFun = BinaryOperator[Any, Any, Symbol]
UnOp = UnaryOperator[Symbol, Symbol]

# Comparison methods (not operator)
eq = CompOp("eq", "symbol", precedence=-5, fmt="{} == {}", output_type=Boolean)
ne = CompOp("ne", "symbol", precedence=-5, fmt="{} != {}", output_type=Boolean)

# Comparison
lt = CompOp("lt", "symbol", precedence=-5, fmt="{} < {}", output_type=Boolean)
le = CompOp("le", "symbol", precedence=-5, fmt="{} <= {}", output_type=Boolean)
gt = CompOp("gt", "symbol", precedence=-5, fmt="{} > {}", output_type=Boolean)
ge = CompOp("ge", "symbol", precedence=-5, fmt="{} >= {}", output_type=Boolean)

# Emulating container types
getitem = BinOp("getitem", "symbol", precedence=5, fmt="{}[{}]", output_type=Symbol)

# Emulating attribute
symgetattr = BinOp(
    "symgetattr", "symbol", precedence=5, fmt="{}.{}", output_type=Symbol
)

# Emulating numeric types
add = BinOp("add", "symbol", precedence=0, fmt="{} + {}", output_type=Symbol)
sub = BinOp("sub", "symbol", precedence=0, fmt="{} - {}", output_type=Symbol)
mul = BinOp("mul", "symbol", precedence=1, fmt="{} * {}", output_type=Symbol)
matmul = BinOp("matmul", "symbol", precedence=1, fmt="{} @ {}", output_type=Symbol)
truediv = BinOp("truediv", "symbol", precedence=1, fmt="{} / {}", output_type=Symbol)
floordiv = BinOp("floordiv", "symbol", precedence=1, fmt="{} // {}", output_type=Symbol)
mod = BinOp("mod", "symbol", precedence=1, fmt="{} % {}", output_type=Symbol)
pow = BinOp("pow", "symbol", precedence=3, fmt="{} ** {}", output_type=Symbol)
pow3 = Function3[Symbol, Symbol]("pow3", "symbol", output_type=Symbol)
lshift = BinOp("lshift", "symbol", precedence=-1, fmt="{} << {}", output_type=Symbol)
rshift = BinOp("rshift", "symbol", precedence=-1, fmt="{} >> {}", output_type=Symbol)
and_ = BinOp("and_", "symbol", precedence=-2, fmt="{} & {}", output_type=Symbol)
xor = BinOp("xor", "symbol", precedence=-3, fmt="{} ^ {}", output_type=Symbol)
or_ = BinOp("or_", "symbol", precedence=-4, fmt="{} | {}", output_type=Symbol)

# Unary operators
neg = UnOp("neg", "symbol", precedence=2, fmt="-{}", output_type=Symbol)
pos = UnOp("pos", "symbol", precedence=2, fmt="+{}", output_type=Symbol)
invert = UnOp("invert", "symbol", precedence=2, fmt="~{}", output_type=Symbol)
