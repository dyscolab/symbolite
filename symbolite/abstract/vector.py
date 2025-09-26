"""
symbolite.abstract.vector
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for vector operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
import warnings
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, overload

from ..core import NamedExpression
from . import symbol
from .real import NumberT, Real
from .symbol import Function, Symbol, downcast

VectorT = Iterable[NumberT]


@dataclasses.dataclass(frozen=True, repr=False)
class Vector(NamedExpression):
    """A user defined symbol."""

    def eq(self, other: Any) -> Symbol:
        return symbol.eq(self, other)

    def ne(self, other: Any) -> Symbol:
        return symbol.ne(self, other)

    def __lt__(self, other: Any) -> Symbol:
        return symbol.lt(self, other)

    def __le__(self, other: Any) -> Symbol:
        return symbol.le(self, other)

    def __gt__(self, other: Any) -> Symbol:
        return symbol.gt(self, other)

    def __ge__(self, other: Any) -> Symbol:
        return symbol.ge(self, other)

    def __getitem__(self, key: int | Real) -> Real:
        return downcast(symbol.getitem(self, key), Real)

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

    def __matmul__(self, other: Vector) -> Real:
        """Implements multiplication."""
        return downcast(symbol.matmul(self, other), Real)

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

    def __rmatmul__(self, other: Any) -> Real:
        """Implements reflected multiplication."""
        return downcast(symbol.matmul(other, self), Real)

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

    def __str__(self) -> str:
        if self.expression is None:
            return super().__str__()
        return str(self.expression)

    def __set_name__(self, owner: Any, name: str):
        if name.endswith("__return"):
            return
        current_name = getattr(self, "name", None)
        if current_name is not None and current_name != name:
            warnings.warn(
                f"Mismatched names in attribute {name}: {type(self)} is named {current_name}"
            )

        object.__setattr__(self, "name", name)


@dataclasses.dataclass(frozen=True, repr=False)
class CumulativeFunction(Function[Real]):
    namespace: str = "vector"
    arity: int = 1

    def __call__(self, arg1: Vector | VectorT) -> Real:
        return super()._call(arg1)  # type: ignore

    @property
    def output_type(self):
        return Real


sum = CumulativeFunction("sum", namespace="vector")
prod = CumulativeFunction("prod", namespace="vector")


@overload
def vectorize(
    expr: NumberT,
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> NumberT: ...


@overload
def vectorize(
    expr: Real,
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> Real: ...


@overload
def vectorize(
    expr: Symbol,
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> Symbol: ...


@overload
def vectorize(
    expr: Iterable[NumberT | Symbol],
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[NumberT | Symbol, ...]: ...


def vectorize(
    expr: NumberT | Symbol | Real | Vector | Iterable[NumberT | Symbol | Real | Vector],
    symbol_names: Sequence[str] | Mapping[str, int],
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> NumberT | Symbol | Real | Vector | tuple[NumberT | Symbol | Real | Vector, ...]:
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

    if not isinstance(expr, (Symbol, Real, Vector)):
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
    scalar_type: type[Real] = Real,
) -> tuple[tuple[str, ...], Symbol]: ...


@overload
def auto_vectorize(
    expr: Symbol,
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[tuple[str, ...], Symbol]: ...


@overload
def auto_vectorize(
    expr: Iterable[Symbol],
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[tuple[str, ...], tuple[Symbol, ...]]: ...


def auto_vectorize(
    expr: NumberT | Symbol | Real | Vector | Iterable[Symbol | Real | Vector],
    varname: str = "vec",
    scalar_type: type[Real] = Real,
) -> tuple[
    tuple[str, ...],
    NumberT | Symbol | Real | Vector | tuple[NumberT | Symbol | Real | Vector, ...],
]:
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

    if not isinstance(expr, (Symbol, Real, Vector)):
        expr = tuple(expr)
        out = set[str]()
        for symbol in expr:
            out.update(_symbol_names(symbol, ""))
        symbol_names = tuple(sorted(out))
        return symbol_names, vectorize(expr, symbol_names, varname, scalar_type)
    else:
        symbol_names = tuple(sorted(_symbol_names(expr, "")))
        return symbol_names, vectorize(expr, symbol_names, varname, scalar_type)
