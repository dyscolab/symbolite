"""
symbolite.impl.libpythoncode.real
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code-emitting counterparts for ``symbolite.abstract.real``.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from ...abstract import real as abstract_real
from ._latexexpr import (
    LatexExpr,
    as_function,
    as_named_value,
    as_operator,
    # make_function,
    nest_sub_and_super_scripts,
)

eq = as_operator(abstract_real.eq)
ne = as_operator(abstract_real.ne)
lt = as_operator(abstract_real.lt)
le = as_operator(abstract_real.le)
gt = as_operator(abstract_real.gt)
ge = as_operator(abstract_real.ge)


def Real(name: str) -> LatexExpr:
    return LatexExpr(nest_sub_and_super_scripts(name))


add = as_operator(abstract_real.add)
sub = as_operator(abstract_real.sub)
mul = as_operator(abstract_real.mul)
truediv = as_operator(abstract_real.truediv)
mod = as_operator(abstract_real.mod)
lshift = as_operator(abstract_real.lshift)
rshift = as_operator(abstract_real.rshift)
and_ = as_operator(abstract_real.and_)
xor = as_operator(abstract_real.xor)
or_ = as_operator(abstract_real.or_)

neg = as_operator(abstract_real.neg)
pos = as_operator(abstract_real.pos)
invert = as_operator(abstract_real.invert)

abs = as_operator(abstract_real.abs)
acos = as_function(abstract_real.acos)
acosh = as_function(abstract_real.acosh)
asin = as_function(abstract_real.asin)
asinh = as_function(abstract_real.asinh)
atan = as_function(abstract_real.atan)
atan2 = as_function(abstract_real.atan2)
atanh = as_function(abstract_real.atanh)
ceil = as_operator(abstract_real.ceil)
comb = as_function(abstract_real.comb)
copysign = as_function(abstract_real.copysign)
cos = as_function(abstract_real.cos)
cosh = as_function(abstract_real.cosh)
degrees = as_function(abstract_real.degrees)
erf = as_function(abstract_real.erf)
erfc = as_function(abstract_real.erfc)
exp = as_function(abstract_real.exp)
expm1 = as_function(abstract_real.expm1)
fabs = abs
factorial = as_operator(abstract_real.factorial)
floor = as_operator(abstract_real.floor)
fmod = as_function(abstract_real.fmod)
frexp = as_function(abstract_real.frexp)
gamma = as_function(abstract_real.gamma)
hypot = as_function(abstract_real.hypot)
isfinite = as_function(abstract_real.isfinite)
isinf = as_function(abstract_real.isinf)
isnan = as_function(abstract_real.isnan)
ldexp = as_function(abstract_real.ldexp)
lgamma = as_function(abstract_real.lgamma)
log = as_function(abstract_real.log)
log10 = as_function(abstract_real.log10)
log1p = as_function(abstract_real.log1p)
log2 = as_function(abstract_real.log2)
modf = as_function(abstract_real.modf)
nextafter = as_function(abstract_real.nextafter)
radians = as_function(abstract_real.radians)
remainder = as_function(abstract_real.remainder)
sin = as_function(abstract_real.sin)
sinh = as_function(abstract_real.sinh)
sqrt = as_operator(abstract_real.sqrt)
tan = as_function(abstract_real.tan)
tanh = as_function(abstract_real.tanh)
trunc = as_function(abstract_real.trunc)
ulp = as_function(abstract_real.ulp)


def floordiv(x, y):
    return floor(truediv(x, y))


def isqrt(x):
    return floor(sqrt(x))


pow = as_operator(abstract_real.pow)

# TODO: what do these other power functions do?
# pow3 = as_function(abstract_real.pow3_op)

# _pow_call = make_function("real.pow")
# _pow_operator = as_operator(abstract_real.pow_op)


# def pow(*args: object, **kwargs: object):
#     if len(args) == 2 and not kwargs:
#         return _pow_operator(*args)
#     return _pow_call(*args, **kwargs)


e = as_named_value(abstract_real.e)
inf = as_named_value(abstract_real.inf)
pi = as_named_value(abstract_real.pi)
nan = as_named_value(abstract_real.nan)
tau = as_named_value(abstract_real.tau)

__all__ = [
    "Real",
    "eq",
    "ne",
    "lt",
    "le",
    "gt",
    "ge",
    "add",
    "sub",
    "mul",
    "truediv",
    "floordiv",
    "mod",
    "lshift",
    "rshift",
    "and_",
    "xor",
    "or_",
    "neg",
    "pos",
    "invert",
    "abs",
    "acos",
    "acosh",
    "asin",
    "asinh",
    "atan",
    "atan2",
    "atanh",
    "ceil",
    "comb",
    "copysign",
    "cos",
    "cosh",
    "degrees",
    "erf",
    "erfc",
    "exp",
    "expm1",
    "fabs",
    "factorial",
    "floor",
    "fmod",
    "frexp",
    "gamma",
    "hypot",
    "isfinite",
    "isinf",
    "isnan",
    "isqrt",
    "ldexp",
    "lgamma",
    "log",
    "log10",
    "log1p",
    "log2",
    "modf",
    "nextafter",
    "radians",
    "remainder",
    "sin",
    "sinh",
    "sqrt",
    "tan",
    "tanh",
    "trunc",
    "ulp",
    "pow",
    #     "pow3",
    "e",
    "inf",
    "pi",
    "nan",
    "tau",
]
