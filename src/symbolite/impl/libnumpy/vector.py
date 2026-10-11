"""
symbolite.impl.libnumpy.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.vector
into values and functions defined in NumPy.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import operator

import numpy as np

from ...core import Unsupported

getitem = operator.getitem

add = np.add
sub = np.subtract
mul = np.multiply
matmul = np.matmul
truediv = np.true_divide
floordiv = np.floor_divide
neg = np.negative
pos = np.positive
invert = np.invert
eq = np.equal
ne = np.not_equal

sum = np.sum
prod = np.prod

Vector = Unsupported


del np, operator, Unsupported
