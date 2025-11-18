"""
symbolite.abstract.vector
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for vector operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, cast, overload

from ..core import Value
from ..core.function import (
    BinaryOperator,
    UnaryFunction,
    UnaryOperator,
)
from .boolean import Boolean
from .real import NumberT, Real
from .symbol import Symbol

VectorT = Iterable[NumberT]


class Vector(Value[VectorT]):
    """Vector Symbolic value.

    See Symbol and Value for information
    """

    def eq(self, other: Any) -> Boolean:
        return eq(self, other)

    def ne(self, other: Any) -> Boolean:
        return ne(self, other)

    def __getitem__(self, key: int | Real) -> Real:
        return getitem(self, key)

    # Normal arithmetic operators
    def __add__(self, other: Any) -> Vector:
        """Implements addition."""
        return add(self, other)

    def __sub__(self, other: Any) -> Vector:
        """Implements subtraction."""
        return sub(self, other)

    def __mul__(self, other: Any) -> Vector:
        """Implements multiplication."""
        return mul(self, other)

    def __matmul__(self, other: Vector) -> Real:
        """Implements multiplication."""
        return matmul(self, other)

    def __truediv__(self, other: Vector) -> Vector:
        """Implements true division."""
        return truediv(self, other)

    def __floordiv__(self, other: Any) -> Vector:
        """Implements integer division using the // operator."""
        return floordiv(self, other)

    # Reflected arithmetic operators
    def __radd__(self, other: Any) -> Vector:
        """Implements reflected addition."""
        return add(other, self)

    def __rsub__(self, other: Any) -> Vector:
        """Implements reflected subtraction."""
        return sub(other, self)

    def __rmul__(self, other: Any) -> Vector:
        """Implements reflected multiplication."""
        return mul(other, self)

    def __rmatmul__(self, other: Any) -> Real:
        """Implements reflected multiplication."""
        return matmul(other, self)

    def __rtruediv__(self, other: Any) -> Vector:
        """Implements reflected true division."""
        return truediv(other, self)

    def __rfloordiv__(self, other: Any) -> Vector:
        """Implements reflected integer division using the // operator."""
        return floordiv(other, self)

    # Unary operators and functions
    def __neg__(self) -> Vector:
        """Implements behavior for negation (e.g. -some_object)"""
        return neg(self)

    def __pos__(self) -> Vector:
        """Implements behavior for unary positive (e.g. +some_object)"""
        return pos(self)

    def __invert__(self) -> Vector:
        """Implements behavior for inversion using the ~ operator."""
        return invert(self)


CompOp = BinaryOperator[Vector | VectorT, Vector | VectorT, Boolean]

# Comparison methods (not operator)
eq = CompOp("eq", "vector", precedence=-5, fmt="{} == {}", output_type=Boolean)
ne = CompOp("ne", "vector", precedence=-5, fmt="{} != {}", output_type=Boolean)

# Emulating container types
getitem = BinaryOperator[Vector, Real | int, Real](
    "getitem", "vector", precedence=5, fmt="{}[{}]", output_type=Real
)

BinOp = BinaryOperator[
    Vector | VectorT | Real | NumberT, Vector | VectorT | Real | NumberT, Vector
]

# Emulating numeric types
add = BinOp("add", "vector", precedence=0, fmt="{} + {}", output_type=Vector)
sub = BinOp("sub", "vector", precedence=0, fmt="{} - {}", output_type=Vector)
mul = BinOp("mul", "vector", precedence=1, fmt="{} * {}", output_type=Vector)
matmul = BinaryOperator[
    Vector | VectorT | Real | NumberT, Vector | VectorT | Real | NumberT, Real
]("matmul", "vector", precedence=1, fmt="{} @ {}", output_type=Real)
truediv = BinOp("truediv", "vector", precedence=1, fmt="{} / {}", output_type=Vector)
floordiv = BinOp("floordiv", "vector", precedence=1, fmt="{} // {}", output_type=Vector)

UnOp = UnaryOperator[Vector, Vector]

# Unary operatorss
neg = UnOp("neg", "vector", precedence=2, fmt="-{}", output_type=Vector)
pos = UnOp("pos", "vector", precedence=2, fmt="+{}", output_type=Vector)
invert = UnOp("invert", "vector", precedence=2, fmt="~{}", output_type=Vector)

sum = UnaryFunction[Vector, Real]("sum", "vector", output_type=Real)
prod = UnaryFunction[Vector, Real]("prod", "vector", output_type=Real)


@overload
def vectorize[T: Value[Any]](
    expr: NumberT,
    input_names: Sequence[str] | Mapping[str, int],
    output_name: str = "vec",
    scalar_type: type[T] = Real,
) -> NumberT: ...


@overload
def vectorize[T: Value[Any]](
    expr: T,
    input_names: Sequence[str] | Mapping[str, int],
    output_name: str = "vec",
    scalar_type: type[T] = Real,
) -> T: ...


@overload
def vectorize[T: Value[Any]](
    expr: Iterable[NumberT | T],
    input_names: Sequence[str] | Mapping[str, int],
    output_name: str = "vec",
    scalar_type: type[T] = Real,
) -> tuple[NumberT | T, ...]: ...


def vectorize[T: Value[Any]](
    expr: NumberT | T | Iterable[NumberT | T],
    input_names: Sequence[str] | Mapping[str, int],
    output_name: str = "vec",
    scalar_type: type[T] = Real,
) -> NumberT | T | Vector | tuple[NumberT | T | Vector, ...]:
    """Vectorize expression by replacing real values
    by an array at a given indices.

    Parameters
    ----------
    expr
    input_names
        if a tuple, provides the names of the values
        which will be mapped to the indices given by their position.
        if a dict, maps symbol names to indices.
    output_name
        name of the array value
    """

    # It would be nice that NumberT is actually the PT of Value.
    if isinstance(expr, NumberT):
        return expr

    if not isinstance(expr, scalar_type):
        # Then is an iterable, vectorize each element.
        expr = cast(Iterable[NumberT | T], expr)
        return tuple(
            vectorize(symbol, input_names, output_name, scalar_type) for symbol in expr
        )

    if isinstance(input_names, dict):
        it = zip(input_names.values(), input_names.keys())
    else:
        it = enumerate(input_names)

    arr = Vector(output_name)

    reps = {scalar_type(name): arr[ndx] for ndx, name in it}
    from ..ops import substitute

    return substitute(expr, reps)


@overload
def auto_vectorize(
    expr: NumberT,
    output_name: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[tuple[str, ...], Real]: ...


@overload
def auto_vectorize(
    expr: Real,
    output_name: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[tuple[str, ...], Real]: ...


@overload
def auto_vectorize(
    expr: Iterable[Real],
    output_name: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[tuple[str, ...], tuple[Real, ...]]: ...


def auto_vectorize(
    expr: NumberT | Real | Iterable[Real],
    output_name: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[
    tuple[str, ...],
    NumberT | Real | tuple[NumberT | Real, ...],
]:
    """Vectorize expression by replacing all test_scalar values
    by an array at a given indices. Symbols are ordered into
    the array alphabetically.

    Parameters
    ----------
    expr
    output_name
        name of the array value

    Returns
    -------
    tuple[str, ...]
        symbol names as ordered in the array.
    SymbolicExpression
        vectorized expression.

    """
    from ..ops.base import value_names as _symbol_names

    if isinstance(expr, NumberT):
        return tuple(), expr

    if not isinstance(expr, (Symbol, Real, Vector)):
        expr = tuple(expr)
        out = set[str]()
        for symbol in expr:
            out.update(_symbol_names(symbol, ""))
        symbol_names = tuple(sorted(out))
        return symbol_names, vectorize(expr, symbol_names, output_name, scalar_type)
    else:
        symbol_names = tuple(sorted(_symbol_names(expr, "")))
        return symbol_names, vectorize(expr, symbol_names, output_name, scalar_type)
