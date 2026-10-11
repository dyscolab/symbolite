"""
symbolite.impl.libsympy.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.vector
into values and functions defined in SymPy.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import builtins
import operator
from typing import Any

import sympy as sy

from ...core import Unsupported

getitem = operator.getitem

# IndexedBase has no whole-vector algebra or known finite reduction domain.
eq = ne = Unsupported
add = sub = mul = matmul = truediv = floordiv = Unsupported
neg = pos = invert = Unsupported


def sum(values: Any) -> Any:
    """Sum explicit finite values; an IndexedBase has no declared extent."""
    if isinstance(values, sy.IndexedBase):
        raise Unsupported(f"vector.sum requires finite values in module {__name__}")
    return builtins.sum(values)


def prod(values: Any) -> Any:
    """Multiply explicit finite values; an IndexedBase has no declared extent."""
    if isinstance(values, sy.IndexedBase):
        raise Unsupported(f"vector.prod requires finite values in module {__name__}")
    return sy.prod(values)


Vector = sy.IndexedBase
