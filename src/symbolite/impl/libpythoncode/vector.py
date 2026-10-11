"""
symbolite.impl.libpythoncode.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code-emitting counterparts for ``symbolite.abstract.vector``.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from ...abstract import vector as abstract_vector
from ._codeexpr import CodeExpr, as_function, as_operator, validate_identifier

eq = as_function(abstract_vector.eq)
ne = as_function(abstract_vector.ne)

# Retain subscript syntax so indexed assignment targets remain valid Python.
getitem = as_operator(abstract_vector.getitem)

add = as_function(abstract_vector.add)
sub = as_function(abstract_vector.sub)
mul = as_function(abstract_vector.mul)
matmul = as_function(abstract_vector.matmul)
truediv = as_function(abstract_vector.truediv)
floordiv = as_function(abstract_vector.floordiv)

neg = as_function(abstract_vector.neg)
pos = as_function(abstract_vector.pos)
invert = as_function(abstract_vector.invert)

sum = as_function(abstract_vector.sum)
prod = as_function(abstract_vector.prod)


def Vector(name: str) -> CodeExpr:
    return CodeExpr(validate_identifier(name, role="value name"))


__all__ = [
    "Vector",
    "add",
    "eq",
    "floordiv",
    "getitem",
    "invert",
    "matmul",
    "mul",
    "ne",
    "neg",
    "pos",
    "prod",
    "sub",
    "sum",
    "truediv",
]
