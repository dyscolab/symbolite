"""
symbolite.impl.libpythoncode.boolean
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code-emitting counterparts for ``symbolite.abstract.boolean``.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from ...abstract import boolean as abstract_boolean
from ._codeexpr import CodeExpr, as_operator

and_ = as_operator(abstract_boolean.and_)
xor = as_operator(abstract_boolean.xor)
or_ = as_operator(abstract_boolean.or_)


def Boolean(name: str) -> CodeExpr:
    return CodeExpr(name)


__all__ = ["Boolean", "and_", "xor", "or_"]
