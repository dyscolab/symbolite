"""
symbolite
~~~~~~~~~

A minimal symbolic python package.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from .abstract import Scalar, Symbol, Vector, scalar, vector
from .abstract.symbol import UserFunction
from .ops import substitute
from .ops.base import evaluate

__all__ = [
    "Symbol",
    "Scalar",
    "scalar",
    "Vector",
    "vector",
    "UserFunction",
    "evaluate",
    "substitute",
]
