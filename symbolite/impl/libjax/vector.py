"""
symbolite.impl.libjax.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.vector
into values and functions defined in JAX.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import operator

import jax.numpy as np

from symbolite.core import Unsupported

op_getitem = operator.getitem

sum = np.sum
prod = np.prod

Vector = Unsupported


del np, operator, Unsupported
