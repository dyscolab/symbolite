"""
symbolite.impl.libjax.scalar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.scalar
into values and functions defined in JAX.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import jax.numpy as np

from symbolite.core import Unsupported

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

Scalar = Unsupported

del np, Unsupported
