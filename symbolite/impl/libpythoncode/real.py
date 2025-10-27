"""
symbolite.impl.libpythoncode.real
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code-emitting counterparts for ``symbolite.abstract.real``.
"""

from __future__ import annotations

from symbolite.abstract import real as abstract_real

from ._codeexpr import (
    CodeExpr,
    as_function,
    as_named_variable,
    as_operator,
    make_function,
)

eq = as_operator(abstract_real.eq)
ne = as_operator(abstract_real.ne)
lt = as_operator(abstract_real.lt)
le = as_operator(abstract_real.le)
gt = as_operator(abstract_real.gt)
ge = as_operator(abstract_real.ge)


def Real(name: str) -> CodeExpr:
    return CodeExpr(name)


add = as_operator(abstract_real.add)
sub = as_operator(abstract_real.sub)
mul = as_operator(abstract_real.mul)
truediv = as_operator(abstract_real.truediv)
floordiv = as_operator(abstract_real.floordiv)
mod = as_operator(abstract_real.mod)
lshift = as_operator(abstract_real.lshift)
rshift = as_operator(abstract_real.rshift)
and_ = as_operator(abstract_real.and_)
xor = as_operator(abstract_real.xor)
or_ = as_operator(abstract_real.or_)

neg = as_operator(abstract_real.neg)
pos = as_operator(abstract_real.pos)
invert = as_operator(abstract_real.invert)

abs = as_function(abstract_real.abs)
acos = as_function(abstract_real.acos)
acosh = as_function(abstract_real.acosh)
asin = as_function(abstract_real.asin)
asinh = as_function(abstract_real.asinh)
atan = as_function(abstract_real.atan)
atan2 = as_function(abstract_real.atan2)
atanh = as_function(abstract_real.atanh)
ceil = as_function(abstract_real.ceil)
comb = as_function(abstract_real.comb)
copysign = as_function(abstract_real.copysign)
cos = as_function(abstract_real.cos)
cosh = as_function(abstract_real.cosh)
degrees = as_function(abstract_real.degrees)
erf = as_function(abstract_real.erf)
erfc = as_function(abstract_real.erfc)
exp = as_function(abstract_real.exp)
expm1 = as_function(abstract_real.expm1)
fabs = as_function(abstract_real.fabs)
factorial = as_function(abstract_real.factorial)
floor = as_function(abstract_real.floor)
fmod = as_function(abstract_real.fmod)
frexp = as_function(abstract_real.frexp)
gamma = as_function(abstract_real.gamma)
hypot = as_function(abstract_real.hypot)
isfinite = as_function(abstract_real.isfinite)
isinf = as_function(abstract_real.isinf)
isnan = as_function(abstract_real.isnan)
isqrt = as_function(abstract_real.isqrt)
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
sqrt = as_function(abstract_real.sqrt)
tan = as_function(abstract_real.tan)
tanh = as_function(abstract_real.tanh)
trunc = as_function(abstract_real.trunc)
ulp = as_function(abstract_real.ulp)

pow3 = as_function(abstract_real.pow3_op)

_pow_call = make_function("real.pow")
_pow_operator = as_operator(abstract_real.pow_op)


def pow(*args: object, **kwargs: object):
    if len(args) == 2 and not kwargs:
        return _pow_operator(*args)
    return _pow_call(*args, **kwargs)


e = as_named_variable(abstract_real.e)
inf = as_named_variable(abstract_real.inf)
pi = as_named_variable(abstract_real.pi)
nan = as_named_variable(abstract_real.nan)
tau = as_named_variable(abstract_real.tau)

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
    "pow3",
    "e",
    "inf",
    "pi",
    "nan",
    "tau",
]
