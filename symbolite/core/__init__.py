"""
symbolite.core
~~~~~~~~~~~~~~

Symbolite core classes and functions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from .expression import Expression, NamedExpression
from .function import Function
from .named import Named
from .symbolgroup import SymbolicNamespace, SymbolicNamespaceMeta


class Unsupported(ValueError):
    """Label unsupported"""


__all__ = ["Named", "Expression", "NamedExpression", "SymbolicNamespace", "SymbolicNamespaceMeta", "Function", "Unsupported"]