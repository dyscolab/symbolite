"""
symbolite.impl.libstd.scalar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.scalar
into values and functions in Python standard library.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import math

from symbolite.core import Unsupported

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

Scalar = Unsupported

del math, Unsupported
