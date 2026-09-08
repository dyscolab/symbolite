"""
symbolite.impl.libsympy.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.vector
into values and functions defined in SymPy.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import operator

import sympy as sy

getitem = operator.getitem

sum = sum  # noqa: PLW0127
prod = sy.prod

Vector = sy.IndexedBase
