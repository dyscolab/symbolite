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

from symbolite.core import Unsupported

op_getitem = operator.getitem

sum = math.fsum
prod = math.prod

Vector = Unsupported
