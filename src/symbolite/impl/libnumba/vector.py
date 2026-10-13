"""
symbolite.impl.libnumba.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.vector
into values and functions defined in NumPy/Numba.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from ..libnumpy.vector import *
import numpy as np
from numba.core.extending import overload


def matmul(a, b):
    return np.matmul(a, b)


@overload(matmul)
def _matmul_ovl(a, b):
    if getattr(a, "ndim", 0) == 1 and getattr(b, "ndim", 0) == 1:
        return lambda a, b: np.sum(a * b)
    elif getattr(a, "ndim", 0) == 2 and getattr(b, "ndim", 0) == 2:
        return lambda a, b: a @ b
    else:
        return lambda a, b: np.dot(a, b)

