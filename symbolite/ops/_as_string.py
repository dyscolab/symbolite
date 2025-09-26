"""
symbolite.core.ops.as_function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from functools import singledispatch
from typing import Any

from ..abstract import Real, Symbol, Vector
from ..core import SymbolicNamespace, SymbolicNamespaceMeta
from .base import assign, free_symbols


@singledispatch
def as_string(expr: Any) -> str:
    """Return the expression as a string.

    Parameters
    ----------
    expr
        symbolic expression.
    """
    return str(expr)


@as_string.register(SymbolicNamespaceMeta)
@as_string.register(SymbolicNamespace)
def _(self) -> str:
    assert isinstance(self, (SymbolicNamespace, SymbolicNamespaceMeta))

    lines = [f"# {self.__name__}", ""]

    for fs in free_symbols(self):
        lines.append(assign(fs.name, f"{fs.__class__.__name__}()"))

    lines.append("")

    for attr_name in dir(self):
        attr = getattr(self, attr_name)
        if not isinstance(attr, (Symbol, Real, Vector)):
            continue

        if attr.expression is not None:
            lines.append(assign(attr_name, f"{attr!s}"))

    return "\n".join(lines)
