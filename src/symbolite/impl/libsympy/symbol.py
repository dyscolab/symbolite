"""
symbolite.impl.libsympy.symbol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.symbol
into values and functions defined in SymPy.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import sympy as sy

from ..libstd.symbol import *

# Mathematical comparisons use SymPy's default relation evaluation.
eq = sy.Eq
ne = sy.Ne

Symbol = sy.Symbol
