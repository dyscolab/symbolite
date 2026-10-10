"""
symbolite.abstract.vector
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for vector operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, overload

from ..core import Value
from ..core.function import (
    BinaryOperator,
    UnaryFunction,
    UnaryOperator,
)
from ..core.symbolite_object import get_symbolite_info
from ..core.value import Name
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
def vectorize[K: Value[Any]](
    expr: Real,
    *,
    into: Vector | None = None,
    order: Sequence[Real | Symbol] | None = None,
    indices: Mapping[K, int] | None = None,
) -> tuple[Vector, Real]: ...


@overload
def vectorize[K: Value[Any]](
    expr: Symbol,
    *,
    into: Vector | None = None,
    order: Sequence[Real | Symbol] | None = None,
    indices: Mapping[K, int] | None = None,
) -> tuple[Vector, Real | Symbol]: ...


@overload
def vectorize[N: NumberT, K: Value[Any]](
    expr: N,
    *,
    into: Vector | None = None,
    order: Sequence[Real | Symbol] | None = None,
    indices: Mapping[K, int] | None = None,
) -> tuple[Vector, N]: ...


@overload
def vectorize[K: Value[Any]](
    expr: Any,
    *,
    into: Vector | None = None,
    order: Sequence[Real | Symbol] | None = None,
    indices: Mapping[K, int] | None = None,
) -> tuple[Vector, Any]: ...


def vectorize[K: Value[Any]](
    expr: Any,
    *,
    into: Vector | None = None,
    order: Sequence[Real | Symbol] | None = None,
    indices: Mapping[K, int] | None = None,
) -> tuple[Vector, Any]:
    """Return a vector and an expression with selected scalars indexed into it.

    Supply exactly one layout: ``order=(x, y)`` assigns consecutive positions
    starting at zero; ``indices={x: 3, y: 5}`` preserves explicit positions
    from any Mapping. Layouts contain actual named Real or Symbol values,
    including subclasses. Unlisted values remain unchanged, and unused layout
    entries are allowed. Repeated values in ``order`` are rejected; shared
    positions in ``indices`` are allowed as explicit aliases.

    Indices must be nonnegative Python integers, excluding bool. Bounds depend
    on the concrete vector supplied during evaluation. ``into=None`` creates a
    fresh anonymous Vector; otherwise the supplied Vector is returned as is.
    The result is always ``(vector, rewritten)``, including constant inputs.
    Expressions and supported containers follow ``substitute``'s structural
    traversal and ownership rules; built-in lists remain lists.
    """
    if (order is None) == (indices is None):
        raise ValueError("Provide exactly one of order or indices.")
    if into is not None and not isinstance(into, Vector):
        raise TypeError("into must be a Vector or None.")

    positions: dict[Real | Symbol, int] = {}
    if order is not None:
        if not isinstance(order, Sequence) or isinstance(order, (str, bytes)):
            raise TypeError("order must be a sequence of named Real or Symbol values.")
        for index, input_value in enumerate(order):
            value = _validate_input(input_value)
            if value in positions:
                raise ValueError("order must not contain repeated values.")
            positions[value] = index
    else:
        if not isinstance(indices, Mapping):
            raise TypeError("indices must be a Mapping of named scalars to integers.")
        for key, index in indices.items():
            value = _validate_input(key)
            if isinstance(index, bool) or not isinstance(index, int):
                raise TypeError("indices must be Python integers, excluding bool.")
            if index < 0:
                raise ValueError("indices must be nonnegative.")
            positions[value] = index

    target = Vector() if into is None else into
    from ..ops import substitute

    return target, substitute(
        expr, {value: target[i] for value, i in positions.items()}
    )


def _validate_input(value: Any) -> Real | Symbol:
    if not isinstance(value, (Real, Symbol)) or not isinstance(
        get_symbolite_info(value).value, Name
    ):
        raise TypeError("Layouts must contain named Real or Symbol values.")
    return value


def vector_inputs(expr: Any) -> tuple[Real | Symbol, ...]:
    """Return the scalar inputs used by auto_vectorize, in vector position order.

    Discover free, unnamespaced Real and Symbol leaves, including subclasses,
    using the same named-object traversal as other operations. Constants such
    as ``real.pi``, existing Vectors, and Boolean leaves are excluded. Each
    structurally distinct input occurs once. Inputs are sorted by name; equal
    names retain their first-occurrence order without merging distinct types.
    Pass namespaced scalar inputs explicitly to ``vectorize`` when needed.
    """
    from ..ops._get_name import get_full_name
    from ..ops.base import free_values

    inputs = (value for value in free_values(expr) if isinstance(value, (Real, Symbol)))
    return tuple(sorted(inputs, key=get_full_name))


@overload
def auto_vectorize(
    expr: Real,
    *,
    into: Vector | None = None,
) -> tuple[Vector, Real]: ...


@overload
def auto_vectorize(
    expr: Symbol,
    *,
    into: Vector | None = None,
) -> tuple[Vector, Real | Symbol]: ...


@overload
def auto_vectorize[N: NumberT](
    expr: N,
    *,
    into: Vector | None = None,
) -> tuple[Vector, N]: ...


@overload
def auto_vectorize(
    expr: Any,
    *,
    into: Vector | None = None,
) -> tuple[Vector, Any]: ...


def auto_vectorize(
    expr: Any,
    *,
    into: Vector | None = None,
) -> tuple[Vector, Any]:
    """Return ``(vector, rewritten)`` using the layout from vector_inputs(expr).

    ``into=None`` creates a fresh anonymous Vector. Supplying ``into`` reuses
    that exact Vector. Inspect ``vector_inputs(expr)`` to pack concrete input
    values in the same deterministic order. Constant inputs have an empty
    layout and still return a Vector alongside the unchanged expression.
    """
    return vectorize(expr, into=into, order=vector_inputs(expr))
