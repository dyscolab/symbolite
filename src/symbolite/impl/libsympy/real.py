"""
symbolite.impl.libsympy.real
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.real
into values and functions defined in SymPy.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import operator as op
from typing import Any

import sympy
import sympy as sy
from sympy.abc import x, y

from ...core import Unsupported

# Comparison methods (not operator)
eq = op.eq
ne = op.ne

# Comparison
lt = op.lt
le = op.le
gt = op.gt
ge = op.ge

# Emulating numeric types
add = op.add
sub = op.sub
mul = op.mul
matmul = op.matmul
truediv = op.truediv
floordiv = op.floordiv
mod = op.mod
pow = op.pow
lshift = op.lshift
rshift = op.rshift
and_ = op.and_
xor = op.xor
or_ = op.or_


def _rev(func: Any) -> Any:
    def _internal(a: Any, b: Any) -> Any:
        return func(b, a)

    return _internal


# Reflective versions
radd = _rev(op.add)
rsub = _rev(op.sub)
rmul = _rev(op.mul)
rmatmul = _rev(op.matmul)
rtruediv = _rev(op.truediv)
rfloordiv = _rev(op.floordiv)
rmod = _rev(op.mod)
rpow = _rev(op.pow)
rlshift = _rev(op.lshift)
rrshift = _rev(op.rshift)
rand = _rev(op.and_)
rxor = _rev(op.xor)
ror = _rev(op.or_)

# Unary operators
neg = op.neg
pos = op.pos
invert = op.inv

abs = sy.Abs
acos = sy.acos
acosh = sy.acosh
asin = sy.asin
asinh = sy.asinh
atan = sy.atan
atan2 = sy.atan2
atanh = sy.atanh
ceil = sy.ceiling
comb = Unsupported
copysign = Unsupported
cos = sy.cos
cosh = sy.cosh
degrees = sy.Lambda(x, x * 180 / sy.pi)
erf = Unsupported
erfc = Unsupported
exp = sy.exp
expm1 = sy.Lambda(x, sy.exp(x) - 1)
fabs = sy.Abs
factorial = Unsupported
floor = sy.floor
fmod = sy.Mod
frexp = Unsupported
gamma = Unsupported
hypot = sy.Lambda((x, y), sy.sqrt(x * x + y * y))
isfinite = Unsupported
isinf = Unsupported
isnan = Unsupported
isqrt = Unsupported
ldexp = Unsupported
lgamma = sy.loggamma
log = sy.log
log10 = sy.Lambda(x, sy.log(x, 10))
log1p = sy.Lambda(x, sy.log(1 + x))
log2 = sy.Lambda(x, sy.log(x, 2))
modf = Unsupported
nextafter = Unsupported
pow = sy.Pow
radians = sy.Lambda(x, x * sy.pi / 180)
remainder = Unsupported
sin = sy.sin
sinh = sy.sinh
sqrt = sy.sqrt
tan = sy.tan
tanh = sy.tanh
trunc = Unsupported
ulp = Unsupported

e = sy.exp(1)
inf = sy.oo
pi = sy.pi
nan = sy.nan
tau = 2 * sy.pi


def Real(name: str):
    return sympy.Symbol(name, real=True)


del sy, Unsupported, x, y
