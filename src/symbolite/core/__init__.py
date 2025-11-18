"""
symbolite.core
~~~~~~~~~~~~~~

Symbolite core classes and functions.

A user should not need to use them directly.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from .call import Call
from .function import Function, Operator
from .symbolgroup import SymbolicNamespace, SymbolicNamespaceMeta
from .value import Value


class Unsupported(ValueError):
    """Label unsupported"""


__all__ = [
    "Call",
    "Value",
    "SymbolicNamespace",
    "SymbolicNamespaceMeta",
    "Function",
    "Operator",
    "Unsupported",
]
