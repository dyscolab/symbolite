"""
symbolite.impl.libpythoncode.symbol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code-emitting counterparts for ``symbolite.abstract.symbol``.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from symbolite.abstract import symbol as abstract_symbol

from ._codeexpr import CodeExpr, as_function, as_operator

eq = as_operator(abstract_symbol.eq)
ne = as_operator(abstract_symbol.ne)
lt = as_operator(abstract_symbol.lt)
le = as_operator(abstract_symbol.le)
gt = as_operator(abstract_symbol.gt)
ge = as_operator(abstract_symbol.ge)

getitem = as_operator(abstract_symbol.getitem)
symgetattr = as_operator(abstract_symbol.symgetattr)

add = as_operator(abstract_symbol.add)
sub = as_operator(abstract_symbol.sub)
mul = as_operator(abstract_symbol.mul)
matmul = as_operator(abstract_symbol.matmul)
truediv = as_operator(abstract_symbol.truediv)
floordiv = as_operator(abstract_symbol.floordiv)
mod = as_operator(abstract_symbol.mod)
pow = as_operator(abstract_symbol.pow)
pow3 = as_function(abstract_symbol.pow3)
lshift = as_operator(abstract_symbol.lshift)
rshift = as_operator(abstract_symbol.rshift)
and_ = as_operator(abstract_symbol.and_)
xor = as_operator(abstract_symbol.xor)
or_ = as_operator(abstract_symbol.or_)

neg = as_operator(abstract_symbol.neg)
pos = as_operator(abstract_symbol.pos)
invert = as_operator(abstract_symbol.invert)


def Symbol(name: str) -> CodeExpr:
    return CodeExpr(name)


__all__ = [
    "Symbol",
    "eq",
    "ne",
    "lt",
    "le",
    "gt",
    "ge",
    "getitem",
    "symgetattr",
    "add",
    "sub",
    "mul",
    "matmul",
    "truediv",
    "floordiv",
    "mod",
    "pow",
    "pow3",
    "lshift",
    "rshift",
    "and_",
    "xor",
    "or_",
    "neg",
    "pos",
    "invert",
]
