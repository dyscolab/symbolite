"""
symbolite.abstract.scalar
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for scalar operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from ..core import Function, Unsupported
from . import symbol
from .symbol import Symbol, downcast

NumberT = int | float | complex


@dataclasses.dataclass(frozen=True, repr=False)
class Scalar(Symbol):
    """A user defined symbol."""

    def __getitem__(self, key: Any):
        return Unsupported

    def __getattr__(self, key: Any):
        raise AttributeError(key)

    # Normal arithmetic operators
    def __add__(self, other: Any) -> Scalar:
        """Implements addition."""
        return downcast(symbol.add(self, other), Scalar)

    def __sub__(self, other: Any) -> Scalar:
        """Implements subtraction."""
        return downcast(symbol.sub(self, other), Scalar)

    def __mul__(self, other: Any) -> Scalar:
        """Implements multiplication."""
        return downcast(symbol.mul(self, other), Scalar)

    def __matmul__(self, other: Any) -> Scalar:
        """Implements multiplication."""
        return downcast(symbol.matmul(self, other), Scalar)

    def __truediv__(self, other: Any) -> Scalar:
        """Implements true division."""
        return downcast(symbol.truediv(self, other), Scalar)

    def __floordiv__(self, other: Any) -> Scalar:
        """Implements integer division using the // operator."""
        return downcast(symbol.floordiv(self, other), Scalar)

    def __mod__(self, other: Any) -> Scalar:
        """Implements modulo using the % operator."""
        return downcast(symbol.mod(self, other), Scalar)

    def __pow__(self, other: Any, modulo: Any = None) -> Scalar:
        """Implements behavior for exponents using the ** operator."""
        if modulo is None:
            return downcast(symbol.pow(self, other), Scalar)
        else:
            return downcast(symbol.pow3(self, other, modulo), Scalar)

    def __lshift__(self, other: Any) -> Scalar:
        """Implements left bitwise shift using the << operator."""
        return downcast(symbol.lshift(self, other), Scalar)

    def __rshift__(self, other: Any) -> Scalar:
        """Implements right bitwise shift using the >> operator."""
        return downcast(symbol.rshift(self, other), Scalar)

    def __and__(self, other: Any) -> Scalar:
        """Implements bitwise and using the & operator."""
        return downcast(symbol.and_(self, other), Scalar)

    def __or__(self, other: Any) -> Scalar:
        """Implements bitwise or using the | operator."""
        return downcast(symbol.or_(self, other), Scalar)

    def __xor__(self, other: Any) -> Scalar:
        """Implements bitwise xor using the ^ operator."""
        return downcast(symbol.xor(self, other), Scalar)

    # Reflected arithmetic operators
    def __radd__(self, other: Any) -> Scalar:
        """Implements reflected addition."""
        return downcast(symbol.add(other, self), Scalar)

    def __rsub__(self, other: Any) -> Scalar:
        """Implements reflected subtraction."""
        return downcast(symbol.sub(other, self), Scalar)

    def __rmul__(self, other: Any) -> Scalar:
        """Implements reflected multiplication."""
        return downcast(symbol.mul(other, self), Scalar)

    def __rmatmul__(self, other: Any) -> Scalar:
        """Implements reflected multiplication."""
        return downcast(symbol.matmul(other, self), Scalar)

    def __rtruediv__(self, other: Any) -> Scalar:
        """Implements reflected true division."""
        return downcast(symbol.truediv(other, self), Scalar)

    def __rfloordiv__(self, other: Any) -> Scalar:
        """Implements reflected integer division using the // operator."""
        return downcast(symbol.floordiv(other, self), Scalar)

    def __rmod__(self, other: Any) -> Scalar:
        """Implements reflected modulo using the % operator."""
        return downcast(symbol.mod(other, self), Scalar)

    def __rpow__(self, other: Any) -> Scalar:
        """Implements behavior for reflected exponents using the ** operator."""
        return downcast(symbol.pow(other, self), Scalar)

    def __rlshift__(self, other: Any) -> Scalar:
        """Implements reflected left bitwise shift using the << operator."""
        return downcast(symbol.lshift(other, self), Scalar)

    def __rrshift__(self, other: Any) -> Scalar:
        """Implements reflected right bitwise shift using the >> operator."""
        return downcast(symbol.rshift(other, self), Scalar)

    def __rand__(self, other: Any) -> Scalar:
        """Implements reflected bitwise and using the & operator."""
        return downcast(symbol.and_(other, self), Scalar)

    def __ror__(self, other: Any) -> Scalar:
        """Implements reflected bitwise or using the | operator."""
        return downcast(symbol.or_(other, self), Scalar)

    def __rxor__(self, other: Any) -> Scalar:
        """Implements reflected bitwise xor using the ^ operator."""
        return downcast(symbol.xor(other, self), Scalar)

    # Unary operators and functions
    def __neg__(self) -> Scalar:
        """Implements behavior for negation (e.g. -some_object)"""
        return downcast(symbol.neg(self), Scalar)

    def __pos__(self) -> Scalar:
        """Implements behavior for unary positive (e.g. +some_object)"""
        return downcast(symbol.pos(self), Scalar)

    def __invert__(self) -> Scalar:
        """Implements behavior for inversion using the ~ operator."""
        return downcast(symbol.invert(self), Scalar)


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class ScalarFunction(Function):
    @property
    def output_type(self) -> type[Scalar]:
        return Scalar


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class ScalarUnaryFunction(ScalarFunction):
    namespace: str = "scalar"
    arity: int = 1

    def __call__(self, arg1: Scalar | NumberT) -> Scalar:
        return super()._call(arg1)  # type: ignore


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class ScalarBinaryFunction(ScalarFunction):
    namespace: str = "scalar"
    arity: int = 2

    def __call__(self, arg1: Scalar | NumberT, arg2: Scalar | NumberT) -> Scalar:
        return super()._call(arg1, arg2)  # type: ignore


# "gcd": None,  # 1 to ---
# "hypot": None,  # 1 to ---
# "isclose": None,  # 2, 3, 4
# "lcm": None,  # 1 to ---
# "perm": None,  # 1 or 2
# "log": None,  # 1 or 2 is used as log(x, e)

abs = ScalarUnaryFunction("abs")
acos = ScalarUnaryFunction("acos")
acosh = ScalarUnaryFunction("acosh")
asin = ScalarUnaryFunction("asin")
asinh = ScalarUnaryFunction("asinh")
atan = ScalarUnaryFunction("atan")
atan2 = ScalarBinaryFunction("atan2")
atanh = ScalarUnaryFunction("atanh")
ceil = ScalarUnaryFunction("ceil")
comb = ScalarUnaryFunction("comb")
copysign = ScalarUnaryFunction("copysign")
cos = ScalarUnaryFunction("cos")
cosh = ScalarUnaryFunction("cosh")
degrees = ScalarUnaryFunction("degrees")
erf = ScalarUnaryFunction("erf")
erfc = ScalarUnaryFunction("erfc")
exp = ScalarUnaryFunction("exp")
expm1 = ScalarUnaryFunction("expm1")
fabs = ScalarUnaryFunction("fabs")
factorial = ScalarUnaryFunction("factorial")
floor = ScalarUnaryFunction("floor")
fmod = ScalarUnaryFunction("fmod")
frexp = ScalarUnaryFunction("frexp")
gamma = ScalarUnaryFunction("gamma")
hypot = ScalarUnaryFunction("gamma")
isfinite = ScalarUnaryFunction("isfinite")
isinf = ScalarUnaryFunction("isinf")
isnan = ScalarUnaryFunction("isnan")
isqrt = ScalarUnaryFunction("isqrt")
ldexp = ScalarBinaryFunction("ldexp")
lgamma = ScalarUnaryFunction("lgamma")
log = ScalarUnaryFunction("log")
log10 = ScalarUnaryFunction("log10")
log1p = ScalarUnaryFunction("log1p")
log2 = ScalarUnaryFunction("log2")
modf = ScalarUnaryFunction("modf")
nextafter = ScalarUnaryFunction("nextafter")
pow = ScalarUnaryFunction("pow")
radians = ScalarUnaryFunction("radians")
remainder = ScalarBinaryFunction("remainder")
sin = ScalarUnaryFunction("sin")
sinh = ScalarUnaryFunction("sinh")
sqrt = ScalarUnaryFunction("sqrt")
tan = ScalarUnaryFunction("tan")
tanh = ScalarUnaryFunction("tanh")
tan = ScalarUnaryFunction("tan")
trunc = ScalarUnaryFunction("trunc")
ulp = ScalarUnaryFunction("ulp")

e = Scalar("e", namespace="scalar")
inf = Scalar("inf", namespace="scalar")
pi = Scalar("pi", namespace="scalar")
nan = Scalar("nan", namespace="scalar")
tau = Scalar("tau", namespace="scalar")

del Function, Symbol, dataclasses
