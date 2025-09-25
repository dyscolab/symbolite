"""
symbolite.abstract.vector
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for vector operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Iterable, Mapping, Sequence, overload

from . import symbol
from .scalar import NumberT, Scalar
from .symbol import Function, Symbol, downcast

VectorT = Iterable[NumberT]


@dataclasses.dataclass(frozen=True, repr=False)
class Vector(Symbol):
    """A user defined symbol."""

    def __getitem__(self, key: int | Scalar) -> Scalar:
        return downcast(super().__getitem__(key), Scalar)

    def __getattr__(self, key: Any):
        raise AttributeError(key)

    # Normal arithmetic operators
    def __add__(self, other: Any) -> Vector:
        """Implements addition."""
        return downcast(symbol.add(self, other), Vector)

    def __sub__(self, other: Any) -> Vector:
        """Implements subtraction."""
        return downcast(symbol.sub(self, other), Vector)

    def __mul__(self, other: Any) -> Vector:
        """Implements multiplication."""
        return downcast(symbol.mul(self, other), Vector)

    def __matmul__(self, other: Vector) -> Scalar:
        """Implements multiplication."""
        return downcast(symbol.matmul(self, other), Scalar)

    def __truediv__(self, other: Vector) -> Vector:
        """Implements true division."""
        return downcast(symbol.truediv(self, other), Vector)

    def __floordiv__(self, other: Any) -> Vector:
        """Implements integer division using the // operator."""
        return downcast(symbol.floordiv(self, other), Vector)

    def __mod__(self, other: Any) -> Vector:
        """Implements modulo using the % operator."""
        return downcast(symbol.mod(self, other), Vector)

    def __pow__(self, other: Any, modulo: Any = None) -> Vector:
        """Implements behavior for exponents using the ** operator."""
        if modulo is None:
            return downcast(symbol.pow(self, other), Vector)
        else:
            return downcast(symbol.pow3(self, other, modulo), Vector)

    def __lshift__(self, other: Any) -> Vector:
        """Implements left bitwise shift using the << operator."""
        return downcast(symbol.lshift(self, other), Vector)

    def __rshift__(self, other: Any) -> Vector:
        """Implements right bitwise shift using the >> operator."""
        return downcast(symbol.rshift(self, other), Vector)

    def __and__(self, other: Any) -> Vector:
        """Implements bitwise and using the & operator."""
        return downcast(symbol.and_(self, other), Vector)

    def __or__(self, other: Any) -> Vector:
        """Implements bitwise or using the | operator."""
        return downcast(symbol.or_(self, other), Vector)

    def __xor__(self, other: Any) -> Vector:
        """Implements bitwise xor using the ^ operator."""
        return downcast(symbol.xor(self, other), Vector)

    # Reflected arithmetic operators
    def __radd__(self, other: Any) -> Vector:
        """Implements reflected addition."""
        return downcast(symbol.add(other, self), Vector)

    def __rsub__(self, other: Any) -> Vector:
        """Implements reflected subtraction."""
        return downcast(symbol.sub(other, self), Vector)

    def __rmul__(self, other: Any) -> Vector:
        """Implements reflected multiplication."""
        return downcast(symbol.mul(other, self), Vector)

    def __rmatmul__(self, other: Any) -> Scalar:
        """Implements reflected multiplication."""
        return downcast(symbol.matmul(other, self), Scalar)

    def __rtruediv__(self, other: Any) -> Vector:
        """Implements reflected true division."""
        return downcast(symbol.truediv(other, self), Vector)

    def __rfloordiv__(self, other: Any) -> Vector:
        """Implements reflected integer division using the // operator."""
        return downcast(symbol.floordiv(other, self), Vector)

    def __rmod__(self, other: Any) -> Vector:
        """Implements reflected modulo using the % operator."""
        return downcast(symbol.mod(other, self), Vector)

    def __rpow__(self, other: Any) -> Vector:
        """Implements behavior for reflected exponents using the ** operator."""
        return downcast(symbol.pow(other, self), Vector)

    def __rlshift__(self, other: Any) -> Vector:
        """Implements reflected left bitwise shift using the << operator."""
        return downcast(symbol.lshift(other, self), Vector)

    def __rrshift__(self, other: Any) -> Vector:
        """Implements reflected right bitwise shift using the >> operator."""
        return downcast(symbol.rshift(other, self), Vector)

    def __rand__(self, other: Any) -> Vector:
        """Implements reflected bitwise and using the & operator."""
        return downcast(symbol.and_(other, self), Vector)

    def __ror__(self, other: Any) -> Vector:
        """Implements reflected bitwise or using the | operator."""
        return downcast(symbol.or_(other, self), Vector)

    def __rxor__(self, other: Any) -> Vector:
        """Implements reflected bitwise xor using the ^ operator."""
        return downcast(symbol.xor(other, self), Vector)

    # Unary operators and functions
    def __neg__(self) -> Vector:
        """Implements behavior for negation (e.g. -some_object)"""
        return downcast(symbol.neg(self), Vector)

    def __pos__(self) -> Vector:
        """Implements behavior for unary positive (e.g. +some_object)"""
        return downcast(symbol.pos(self), Vector)

    def __invert__(self) -> Vector:
        """Implements behavior for inversion using the ~ operator."""
        return downcast(symbol.invert(self), Vector)


@dataclasses.dataclass(frozen=True, repr=False)
class CumulativeFunction(Function):
    namespace: str = "vector"
    arity: int = 1

    def __call__(self, arg1: Vector | VectorT) -> Scalar:
        return super()._call(arg1)  # type: ignore

    @property
    def output_type(self):
        return Scalar


sum = CumulativeFunction("sum", namespace="vector")
prod = CumulativeFunction("prod", namespace="vector")


@overload
def vectorize(
    expr: NumberT,
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> NumberT: ...


@overload
def vectorize(
    expr: Symbol,
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> Symbol: ...


@overload
def vectorize(
    expr: Iterable[NumberT | Symbol],
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> tuple[NumberT | Symbol, ...]: ...


def vectorize(
    expr: NumberT | Symbol | Iterable[NumberT | Symbol],
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> NumberT | Symbol | tuple[NumberT | Symbol, ...]:
    """Vectorize expression by replacing scalar symbols
    by an array at a given indices.

    Parameters
    ----------
    expr
    symbol_names
        if a tuple, provides the names of the symbols
        which will be mapped to the indices given by their position.
        if a dict, maps symbol names to indices.
    varname
        name of the array variable
    """
    if isinstance(expr, NumberT):
        return expr

    if not isinstance(expr, Symbol):
        return tuple(vectorize(symbol, symbol_names, varname) for symbol in expr)

    if isinstance(symbol_names, dict):
        it = zip(symbol_names.values(), symbol_names.keys())
    else:
        it = enumerate(symbol_names)

    arr = Vector(varname)

    reps = {scalar_type(name): arr[ndx] for ndx, name in it}
    from ..ops import substitute
    return substitute(expr, reps)


@overload
def auto_vectorize(
    expr: NumberT,
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> tuple[tuple[str, ...], Symbol]: ...


@overload
def auto_vectorize(
    expr: Symbol,
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> tuple[tuple[str, ...], Symbol]: ...


@overload
def auto_vectorize(
    expr: Iterable[Symbol],
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> tuple[tuple[str, ...], tuple[Symbol, ...]]: ...


def auto_vectorize(
    expr: NumberT | Symbol | Iterable[Symbol],
    varname: str = "vec",
    scalar_type: type[Scalar] = Scalar,
) -> tuple[tuple[str, ...], NumberT | Symbol | tuple[NumberT | Symbol, ...]]:
    """Vectorize expression by replacing all test_scalar symbols
    by an array at a given indices. Symbols are ordered into
    the array alphabetically.

    Parameters
    ----------
    expr
    varname
        name of the array variable

    Returns
    -------
    tuple[str, ...]
        symbol names as ordered in the array.
    SymbolicExpression
        vectorized expression.
    """
    from ..ops.base import symbol_names as _symbol_names

    if isinstance(expr, NumberT):
        return tuple(), expr

    if not isinstance(expr, Symbol):
        expr = tuple(expr)
        out = set[str]()
        for symbol in expr:
            out.update(_symbol_names(symbol, ""))
        symbol_names = tuple(sorted(out))
        return symbol_names, vectorize(expr, symbol_names, varname, scalar_type)
    else:
        symbol_names = tuple(sorted(_symbol_names(expr, "")))
        return symbol_names, vectorize(expr, symbol_names, varname, scalar_type)
