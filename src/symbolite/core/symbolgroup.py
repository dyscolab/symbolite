"""
symbolite.core.symbolgroup
~~~~~~~~~~~~~~~~~~~~~~~~~~

Groups of symbols and symbolic expressions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

# class StatementList(list[Statement]):
#     pass


# This is necessary to use singledispatch on classes.
class SymbolicNamespaceMeta(type):
    pass


class SymbolicNamespace(metaclass=SymbolicNamespaceMeta):
    pass
