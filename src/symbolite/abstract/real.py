"""
symbolite.abstract.real
~~~~~~~~~~~~~~~~~~~~~~~

Objects and functions for real number operations.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from typing import Any

from ..core import Value
from ..core.function import (
    BinaryFunction,
    BinaryOperator,
    Function3,
    UnaryFunction,
    UnaryOperator,
)
from .boolean import Boolean

NumberT = int | float


class Real(Value[NumberT]):
    """Real number symbolic value.

    See Symbol and Value for more information.
    """

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


CompOp = BinaryOperator[Real | NumberT, Real | NumberT, Boolean]

# Comparison methods (not operator)
eq = CompOp("eq", "real", precedence=-5, fmt="{} == {}", output_type=Boolean)
ne = CompOp("ne", "real", precedence=-5, fmt="{} != {}", output_type=Boolean)

# Comparison
lt = CompOp("lt", "real", precedence=-5, fmt="{} < {}", output_type=Boolean)
le = CompOp("le", "real", precedence=-5, fmt="{} <= {}", output_type=Boolean)
gt = CompOp("gt", "real", precedence=-5, fmt="{} > {}", output_type=Boolean)
ge = CompOp("ge", "real", precedence=-5, fmt="{} >= {}", output_type=Boolean)

BinOp = BinaryOperator[Real | NumberT, Real | NumberT, Real]

# Emulating numeric types
add = BinOp("add", "real", precedence=0, fmt="{} + {}", output_type=Real)
sub = BinOp("sub", "real", precedence=0, fmt="{} - {}", output_type=Real)
mul = BinOp("mul", "real", precedence=1, fmt="{} * {}", output_type=Real)
truediv = BinOp("truediv", "real", precedence=1, fmt="{} / {}", output_type=Real)
floordiv = BinOp("floordiv", "real", precedence=1, fmt="{} // {}", output_type=Real)
mod = BinOp("mod", "real", precedence=1, fmt="{} % {}", output_type=Real)
pow_op = BinOp("pow", "real", precedence=3, fmt="{} ** {}", output_type=Real)
pow3_op = Function3[Real, Real]("pow3", "real", output_type=Real)
lshift = BinOp("lshift", "real", precedence=-1, fmt="{} << {}", output_type=Real)
rshift = BinOp("rshift", "real", precedence=-1, fmt="{} >> {}", output_type=Real)
and_ = BinOp("and_", "real", precedence=-2, fmt="{} & {}", output_type=Real)
xor = BinOp("xor", "real", precedence=-3, fmt="{} ^ {}", output_type=Real)
or_ = BinOp("or_", "real", precedence=-4, fmt="{} | {}", output_type=Real)

UnOp = UnaryOperator[Real, Real]

# Unary operators
neg = UnOp("neg", "real", precedence=2, fmt="-{}", output_type=Real)
pos = UnOp("pos", "real", precedence=2, fmt="+{}", output_type=Real)
invert = UnOp("invert", "real", precedence=2, fmt="~{}", output_type=Real)

UnFun = UnaryFunction[Real | NumberT, Real]
BinFun = BinaryFunction[Real | NumberT, Real]

# "gcd": None,  # 1 to ---
# "hypot": None,  # 1 to ---
# "isclose": None,  # 2, 3, 4
# "lcm": None,  # 1 to ---
# "perm": None,  # 1 or 2
# "log": None,  # 1 or 2 is used as log(x, e)

abs = UnFun("abs", "real", output_type=Real)
acos = UnFun("acos", "real", output_type=Real)
acosh = UnFun("acosh", "real", output_type=Real)
asin = UnFun("asin", "real", output_type=Real)
asinh = UnFun("asinh", "real", output_type=Real)
atan = UnFun("atan", "real", output_type=Real)
atan2 = BinFun("atan2", "real", output_type=Real)
atanh = UnFun("atanh", "real", output_type=Real)
ceil = UnFun("ceil", "real", output_type=Real)
comb = UnFun("comb", "real", output_type=Real)
copysign = UnFun("copysign", "real", output_type=Real)
cos = UnFun("cos", "real", output_type=Real)
cosh = UnFun("cosh", "real", output_type=Real)
degrees = UnFun("degrees", "real", output_type=Real)
erf = UnFun("erf", "real", output_type=Real)
erfc = UnFun("erfc", "real", output_type=Real)
exp = UnFun("exp", "real", output_type=Real)
expm1 = UnFun("expm1", "real", output_type=Real)
fabs = UnFun("fabs", "real", output_type=Real)
factorial = UnFun("factorial", "real", output_type=Real)
floor = UnFun("floor", "real", output_type=Real)
fmod = UnFun("fmod", "real", output_type=Real)
frexp = UnFun("frexp", "real", output_type=Real)
gamma = UnFun("gamma", "real", output_type=Real)
hypot = UnFun("gamma", "real", output_type=Real)
isfinite = UnFun("isfinite", "real", output_type=Real)
isinf = UnFun("isinf", "real", output_type=Real)
isnan = UnFun("isnan", "real", output_type=Real)
isqrt = UnFun("isqrt", "real", output_type=Real)
ldexp = BinFun("ldexp", "real", output_type=Real)
lgamma = UnFun("lgamma", "real", output_type=Real)
log = UnFun("log", "real", output_type=Real)
log10 = UnFun("log10", "real", output_type=Real)
log1p = UnFun("log1p", "real", output_type=Real)
log2 = UnFun("log2", "real", output_type=Real)
modf = UnFun("modf", "real", output_type=Real)
nextafter = UnFun("nextafter", "real", output_type=Real)
pow = BinFun("pow", "real", output_type=Real)
radians = UnFun("radians", "real", output_type=Real)
remainder = BinFun("remainder", "real", output_type=Real)
sin = UnFun("sin", "real", output_type=Real)
sinh = UnFun("sinh", "real", output_type=Real)
sqrt = UnFun("sqrt", "real", output_type=Real)
tan = UnFun("tan", "real", output_type=Real)
tanh = UnFun("tanh", "real", output_type=Real)
tan = UnFun("tan", "real", output_type=Real)
trunc = UnFun("trunc", "real", output_type=Real)
ulp = UnFun("ulp", "real", output_type=Real)

e = Real("real.e")
inf = Real("real.inf")
pi = Real("real.pi")
nan = Real("real.nan")
tau = Real("rea.tau")

del (
    BinaryFunction,
    BinaryOperator,
    UnaryFunction,
    UnaryOperator,
    CompOp,
    BinOp,
    UnOp,
    BinFun,
    UnFun,
)
