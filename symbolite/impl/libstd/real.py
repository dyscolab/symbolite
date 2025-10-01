"""
symbolite.impl.libstd.real
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.real
into values and functions in Python standard library.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import math
import operator as op
import typing as ty

from symbolite.core import Unsupported

_pow = pow


# Comparison methods (not operator)
eq = op.eq
ne = op.ne

# Comparison
lt = op.lt
le = op.le
gt = op.gt
ge = op.ge

# Emulating container types
getitem = op.getitem
symgetattr = getattr

# Emulating numeric types
add = op.add
sub = op.sub
mul = op.mul
matmul = op.matmul
truediv = op.truediv
floordiv = op.floordiv
mod = op.mod
pow = op.pow
pow3 = _pow
lshift = op.lshift
rshift = op.rshift
and_ = op.and_
xor = op.xor
or_ = op.or_


def _rev(func: ty.Any) -> ty.Any:
    def _internal(a: ty.Any, b: ty.Any) -> ty.Any:
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

# "gcd": None,  # 1 to ---
# "hypot": None,  # 1 to ---
# "isclose": None,  # 2, 3, 4
# "lcm": None,  # 1 to ---
# "perm": None,  # 1 or 2
# "log": None,  # 1 or 2 is used as log(x, e)

abs = abs
acos = math.acos
acosh = math.acosh
asin = math.asin
asinh = math.asinh
atan = math.atan
atan2 = math.atan2
atanh = math.atanh
ceil = math.ceil
comb = math.comb
copysign = math.copysign
cos = math.cos
cosh = math.cosh
degrees = math.degrees
erf = math.erf
erfc = math.erfc
exp = math.exp
expm1 = math.expm1
fabs = math.fabs
factorial = math.factorial
floor = math.floor
fmod = math.fmod
frexp = math.frexp
gamma = math.gamma
hypot = math.hypot
isfinite = math.isfinite
isinf = math.isinf
isnan = math.isnan
isqrt = math.isqrt
ldexp = math.ldexp
lgamma = math.lgamma
log = math.log
log10 = math.log10
log1p = math.log1p
log2 = math.log2
modf = math.modf
nextafter = math.nextafter
log2 = math.log2
pow = math.pow
radians = math.radians
remainder = math.remainder
sin = math.sin
sinh = math.sinh
sqrt = math.sqrt
tan = math.tan
tanh = math.tanh
tan = math.tan
trunc = math.trunc
ulp = math.ulp

e = math.e
inf = math.inf
pi = math.pi
nan = math.nan
tau = math.tau

Real = Unsupported

del math, Unsupported, _rev, op, _pow
