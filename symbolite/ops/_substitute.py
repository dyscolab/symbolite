"""
symbolite.core.ops.substitute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace symbols, functions, values, etc by others.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import inspect
from functools import singledispatch
from typing import Any, Mapping

from ..abstract import Symbol
from ..core import Expression, SymbolicNamespace, SymbolicNamespaceMeta


@singledispatch
def substitute(expr: Any, replacements: Mapping[Any, Any]) -> Any:
    """Replace symbols, functions, values, etc by others.

    Parameters
    ----------
    expr
        symbolic expression.
    replacements
        replacement dictionary.
    """
    return replacements.get(expr, expr)

@substitute.register
def substitute_symbol(self: Symbol, mapper: Mapping[Any, Any]) -> Symbol:
    if self.expression is None:
        return mapper.get(self, self)
    out = substitute(self.expression, mapper)
    if not isinstance(out, Expression):
        return out
    return self.__class__(name=self.name, namespace=self.namespace, expression=out)

@substitute.register
def substitue_expression(self: Expression, mapper: Mapping[Any, Any]) -> Expression:
    func = mapper.get(self.func, self.func)
    args = tuple(substitute(arg, mapper) for arg in self.args)
    kwargs = {k: substitute(arg, mapper) for k, arg in self.kwargs_items}

    return Expression(func, args, tuple(kwargs.items()))

@substitute.register(SymbolicNamespaceMeta)
@substitute.register(SymbolicNamespace)
def _(self, replacements: Mapping[Any, Any]) -> Any:
    assert isinstance(self, (SymbolicNamespace, SymbolicNamespaceMeta))

    d = {}
    for attr_name in dir(self):
        if attr_name.startswith("__"):
            continue
        attr = getattr(self, attr_name)
        d[attr_name] = substitute(attr, replacements)

    return type(self.__name__, inspect.getmro(self), d)

