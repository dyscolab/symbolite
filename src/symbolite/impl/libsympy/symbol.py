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

Symbol = sy.Symbol
