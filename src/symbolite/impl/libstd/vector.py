"""
symbolite.impl.libstd.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.vector
into values and functions defined in Python's math module.

:copyright: 2023 by Symbolite-array Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import math
import operator
from collections.abc import Callable
from typing import Any

from ...core import Unsupported

getitem = operator.getitem


def _native(func: Callable[..., Any]) -> Callable[..., Any]:
    def apply(*values: Any) -> Any:
        if any(isinstance(value, (list, tuple)) for value in values):
            raise TypeError(
                f"vector.{func.__name__} requires native vector operators; "
                "Python lists and tuples support only indexing and reductions "
                "in libstd."
            )
        return func(*values)

    return apply


eq = _native(operator.eq)
ne = _native(operator.ne)
add = _native(operator.add)
sub = _native(operator.sub)
mul = _native(operator.mul)
matmul = _native(operator.matmul)
truediv = _native(operator.truediv)
floordiv = _native(operator.floordiv)
neg = _native(operator.neg)
pos = _native(operator.pos)
invert = _native(operator.invert)

sum = math.fsum
prod = math.prod

Vector = Unsupported
