"""
symbolite.impl.libnumpy.real
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.real
into values and functions defined in NumPy.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import operator as op
from typing import Any

import numpy as np

from symbolite.core import Unsupported

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

abs = np.abs
acos = np.arccos
acosh = np.arccosh
asin = np.arcsin
asinh = np.arcsinh
atan = np.arctan
atan2 = np.arctan2
atanh = np.arctanh
ceil = np.ceil
comb = Unsupported
copysign = np.copysign
cos = np.cos
cosh = np.cosh
degrees = np.degrees
erf = Unsupported
erfc = Unsupported
exp = np.exp
expm1 = np.expm1
fabs = np.fabs
factorial = Unsupported
floor = np.floor
fmod = np.fmod
frexp = np.frexp
gamma = Unsupported
hypot = np.hypot
isfinite = np.isfinite
isinf = np.isinf
isnan = np.isnan
isqrt = Unsupported
ldexp = np.ldexp
lgamma = Unsupported
log = np.log
log10 = np.log10
log1p = np.log1p
log2 = np.log2
modf = np.modf
nextafter = np.nextafter
pow = np.power
radians = np.radians
remainder = np.remainder
sin = np.sin
sinh = np.sinh
sqrt = np.sqrt
tan = np.tan
tanh = np.tanh
trunc = np.trunc
ulp = Unsupported

e = np.e
inf = np.inf
pi = np.pi
nan = np.nan
tau = 2 * np.pi

Real = Unsupported

del np, Unsupported
