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

from symbolite.core import Unsupported

op_getitem = operator.getitem

sum = np.sum
prod = np.prod

Vector = Unsupported


del np, operator, Unsupported
