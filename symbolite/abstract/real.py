"""
symbolite.abstract.real
~~~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for real number operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from ..core import NamedExpression
from ..core.function import (
    BinaryFunction,
    BinaryOperator,
    Function3,
    UnaryFunction,
    UnaryOperator,
)
from .boolean import Boolean

NumberT = int | float | complex


@dataclasses.dataclass(frozen=True, repr=False)
class Real(NamedExpression):
    """A user defined symbol."""

    def eq(self, other: Any) -> Boolean:
        return eq(self, other)

    def ne(self, other: Any) -> Boolean:
        return ne(self, other)

    def __lt__(self, other: Any) -> Boolean:
        return lt(self, other)

    def __le__(self, other: Any) -> Boolean:
        return le(self, other)

    def __gt__(self, other: Any) -> Boolean:
        return gt(self, other)

    def __ge__(self, other: Any) -> Boolean:
        return ge(self, other)

    # Normal arithmetic operators
    def __add__(self, other: Any) -> Real:
        """Implements addition."""
        return add(self, other)

    def __sub__(self, other: Any) -> Real:
        """Implements subtraction."""
        return sub(self, other)

    def __mul__(self, other: Any) -> Real:
        """Implements multiplication."""
        return mul(self, other)

    def __matmul__(self, other: Any) -> Real:
        """Implements multiplication."""
        return matmul(self, other)

    def __truediv__(self, other: Any) -> Real:
        """Implements true division."""
        return truediv(self, other)

    def __floordiv__(self, other: Any) -> Real:
        """Implements integer division using the // operator."""
        return floordiv(self, other)

    def __mod__(self, other: Any) -> Real:
        """Implements modulo using the % operator."""
        return mod(self, other)

    def __pow__(self, other: Any, modulo: Any = None) -> Real:
        """Implements behavior for exponents using the ** operator."""
        if modulo is None:
            return pow_op(self, other)
        else:
            return pow3_op(self, other, modulo)

    def __lshift__(self, other: Any) -> Real:
        """Implements left bitwise shift using the << operator."""
        return lshift(self, other)

    def __rshift__(self, other: Any) -> Real:
        """Implements right bitwise shift using the >> operator."""
        return rshift(self, other)

    def __and__(self, other: Any) -> Real:
        """Implements bitwise and using the & operator."""
        return and_(self, other)

    def __or__(self, other: Any) -> Real:
        """Implements bitwise or using the | operator."""
        return or_(self, other)

    def __xor__(self, other: Any) -> Real:
        """Implements bitwise xor using the ^ operator."""
        return xor(self, other)

    # Reflected arithmetic operators
    def __radd__(self, other: Any) -> Real:
        """Implements reflected addition."""
        return add(other, self)

    def __rsub__(self, other: Any) -> Real:
        """Implements reflected subtraction."""
        return sub(other, self)

    def __rmul__(self, other: Any) -> Real:
        """Implements reflected multiplication."""
        return mul(other, self)

    def __rmatmul__(self, other: Any) -> Real:
        """Implements reflected multiplication."""
        return matmul(other, self)

    def __rtruediv__(self, other: Any) -> Real:
        """Implements reflected true division."""
        return truediv(other, self)

    def __rfloordiv__(self, other: Any) -> Real:
        """Implements reflected integer division using the // operator."""
        return floordiv(other, self)

    def __rmod__(self, other: Any) -> Real:
        """Implements reflected modulo using the % operator."""
        return mod(other, self)

    def __rpow__(self, other: Any) -> Real:
        """Implements behavior for reflected exponents using the ** operator."""
        return pow_op(other, self)

    def __rlshift__(self, other: Any) -> Real:
        """Implements reflected left bitwise shift using the << operator."""
        return lshift(other, self)

    def __rrshift__(self, other: Any) -> Real:
        """Implements reflected right bitwise shift using the >> operator."""
        return rshift(other, self)

    def __rand__(self, other: Any) -> Real:
        """Implements reflected bitwise and using the & operator."""
        return and_(other, self)

    def __ror__(self, other: Any) -> Real:
        """Implements reflected bitwise or using the | operator."""
        return or_(other, self)

    def __rxor__(self, other: Any) -> Real:
        """Implements reflected bitwise xor using the ^ operator."""
        return xor(other, self)

    # Unary operators and functions
    def __neg__(self) -> Real:
        """Implements behavior for negation (e.g. -some_object)"""
        return neg(self)

    def __pos__(self) -> Real:
        """Implements behavior for unary positive (e.g. +some_object)"""
        return pos(self)

    def __invert__(self) -> Real:
        """Implements behavior for inversion using the ~ operator."""
        return invert(self)

    def __str__(self) -> str:
        from ..ops import as_string

        if self.expression is None:
            return super().__str__()
        return as_string(self.expression)

    def __set_name__(self, owner: Any, name: str):
        if name.endswith("__return"):
            return
        current_name = getattr(self, "name", None)
        import warnings

        if current_name is not None and current_name != name:
            warnings.warn(
                f"Mismatched names in attribute {name}: {type(self)} is named {current_name}"
            )

        object.__setattr__(self, "name", name)


CompOp = BinaryOperator[Real, Boolean]

# Comparison methods (not operator)
eq = CompOp("eq", "real", precedence=-5, fmt="{} == {}", result_cls=Boolean)
ne = CompOp("ne", "real", precedence=-5, fmt="{} != {}", result_cls=Boolean)

# Comparison
lt = CompOp("lt", "real", precedence=-5, fmt="{} < {}", result_cls=Boolean)
le = CompOp("le", "real", precedence=-5, fmt="{} <= {}", result_cls=Boolean)
gt = CompOp("gt", "real", precedence=-5, fmt="{} > {}", result_cls=Boolean)
ge = CompOp("ge", "real", precedence=-5, fmt="{} >= {}", result_cls=Boolean)

BinOp = BinaryOperator[Real | NumberT, Real]

# Emulating numeric types
add = BinOp("add", "real", precedence=0, fmt="{} + {}", result_cls=Real)
sub = BinOp("sub", "real", precedence=0, fmt="{} - {}", result_cls=Real)
mul = BinOp("mul", "real", precedence=1, fmt="{} * {}", result_cls=Real)
matmul = BinOp("matmul", "real", precedence=1, fmt="{} @ {}", result_cls=Real)
truediv = BinOp("truediv", "real", precedence=1, fmt="{} / {}", result_cls=Real)
floordiv = BinOp("floordiv", "real", precedence=1, fmt="{} // {}", result_cls=Real)
mod = BinOp("mod", "real", precedence=1, fmt="{} % {}", result_cls=Real)
pow_op = BinOp("pow", "real", precedence=3, fmt="{} ** {}", result_cls=Real)
pow3_op = Function3[Real, Real](
    "pow3", "real", fmt="pow({}, {}, {})", arity=3, result_cls=Real
)
lshift = BinOp("lshift", "real", precedence=-1, fmt="{} << {}", result_cls=Real)
rshift = BinOp("rshift", "real", precedence=-1, fmt="{} >> {}", result_cls=Real)
and_ = BinOp("and_", "real", precedence=-2, fmt="{} & {}", result_cls=Real)
xor = BinOp("xor", "real", precedence=-3, fmt="{} ^ {}", result_cls=Real)
or_ = BinOp("or_", "real", precedence=-4, fmt="{} | {}", result_cls=Real)

UnOp = UnaryOperator[Real, Real]

# Unary operators
neg = UnOp("neg", "real", precedence=2, fmt="-{}", result_cls=Real)
pos = UnOp("pos", "real", precedence=2, fmt="+{}", result_cls=Real)
invert = UnOp("invert", "real", precedence=2, fmt="~{}", result_cls=Real)

UnFun = UnaryFunction[Real | NumberT, Real]
BinFun = BinaryFunction[Real | NumberT, Real]

# "gcd": None,  # 1 to ---
# "hypot": None,  # 1 to ---
# "isclose": None,  # 2, 3, 4
# "lcm": None,  # 1 to ---
# "perm": None,  # 1 or 2
# "log": None,  # 1 or 2 is used as log(x, e)

abs = UnFun("abs", "real", result_cls=Real)
acos = UnFun("acos", "real", result_cls=Real)
acosh = UnFun("acosh", "real", result_cls=Real)
asin = UnFun("asin", "real", result_cls=Real)
asinh = UnFun("asinh", "real", result_cls=Real)
atan = UnFun("atan", "real", result_cls=Real)
atan2 = BinFun("atan2", "real", result_cls=Real)
atanh = UnFun("atanh", "real", result_cls=Real)
ceil = UnFun("ceil", "real", result_cls=Real)
comb = UnFun("comb", "real", result_cls=Real)
copysign = UnFun("copysign", "real", result_cls=Real)
cos = UnFun("cos", "real", result_cls=Real)
cosh = UnFun("cosh", "real", result_cls=Real)
degrees = UnFun("degrees", "real", result_cls=Real)
erf = UnFun("erf", "real", result_cls=Real)
erfc = UnFun("erfc", "real", result_cls=Real)
exp = UnFun("exp", "real", result_cls=Real)
expm1 = UnFun("expm1", "real", result_cls=Real)
fabs = UnFun("fabs", "real", result_cls=Real)
factorial = UnFun("factorial", "real", result_cls=Real)
floor = UnFun("floor", "real", result_cls=Real)
fmod = UnFun("fmod", "real", result_cls=Real)
frexp = UnFun("frexp", "real", result_cls=Real)
gamma = UnFun("gamma", "real", result_cls=Real)
hypot = UnFun("gamma", "real", result_cls=Real)
isfinite = UnFun("isfinite", "real", result_cls=Real)
isinf = UnFun("isinf", "real", result_cls=Real)
isnan = UnFun("isnan", "real", result_cls=Real)
isqrt = UnFun("isqrt", "real", result_cls=Real)
ldexp = BinFun("ldexp", "real", result_cls=Real)
lgamma = UnFun("lgamma", "real", result_cls=Real)
log = UnFun("log", "real", result_cls=Real)
log10 = UnFun("log10", "real", result_cls=Real)
log1p = UnFun("log1p", "real", result_cls=Real)
log2 = UnFun("log2", "real", result_cls=Real)
modf = UnFun("modf", "real", result_cls=Real)
nextafter = UnFun("nextafter", "real", result_cls=Real)
pow = UnFun("pow", "real", result_cls=Real)
radians = UnFun("radians", "real", result_cls=Real)
remainder = BinFun("remainder", "real", result_cls=Real)
sin = UnFun("sin", "real", result_cls=Real)
sinh = UnFun("sinh", "real", result_cls=Real)
sqrt = UnFun("sqrt", "real", result_cls=Real)
tan = UnFun("tan", "real", result_cls=Real)
tanh = UnFun("tanh", "real", result_cls=Real)
tan = UnFun("tan", "real", result_cls=Real)
trunc = UnFun("trunc", "real", result_cls=Real)
ulp = UnFun("ulp", "real", result_cls=Real)

e = Real("e", namespace="real")
inf = Real("inf", namespace="real")
pi = Real("pi", namespace="real")
nan = Real("nan", namespace="real")
tau = Real("tau", namespace="real")

del (
    dataclasses,
    BinaryFunction,
    BinaryOperator,
    UnaryFunction,
    UnaryOperator,
    NamedExpression,
    CompOp,
    BinOp,
    UnOp,
    BinFun,
    UnFun,
)
