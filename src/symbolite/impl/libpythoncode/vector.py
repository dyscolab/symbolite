"""
symbolite.impl.libpythoncode.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code-emitting counterparts for ``symbolite.abstract.vector``.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from symbolite.abstract import vector as abstract_vector

from ._codeexpr import CodeExpr, as_function, as_operator

eq = as_operator(abstract_vector.eq)
ne = as_operator(abstract_vector.ne)

getitem = as_operator(abstract_vector.getitem)

add = as_operator(abstract_vector.add)
sub = as_operator(abstract_vector.sub)
mul = as_operator(abstract_vector.mul)
matmul = as_operator(abstract_vector.matmul)
truediv = as_operator(abstract_vector.truediv)
floordiv = as_operator(abstract_vector.floordiv)

neg = as_operator(abstract_vector.neg)
pos = as_operator(abstract_vector.pos)
invert = as_operator(abstract_vector.invert)

sum = as_function(abstract_vector.sum)
prod = as_function(abstract_vector.prod)


def Vector(name: str) -> CodeExpr:
    return CodeExpr(name)


__all__ = [
    "eq",
    "ne",
    "getitem",
    "add",
    "sub",
    "mul",
    "matmul",
    "truediv",
    "floordiv",
    "neg",
    "pos",
    "invert",
    "sum",
    "prod",
    "Vector",
]
