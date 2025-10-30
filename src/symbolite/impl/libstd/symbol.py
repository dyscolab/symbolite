"""
symbolite.impl.libstd.symbol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.symbol
into values and functions in Python standard library.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import operator as op
import typing as ty

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


del _rev, op, _pow
