"""
symbolite.core.ops.substitute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace symbols, functions, values, etc by others.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import inspect
from collections.abc import Mapping
from functools import singledispatch
from typing import Any, cast

from ..abstract import Scalar, Symbol, Vector
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


def _substitute_named_expression(
    self: Symbol | Scalar | Vector,
    mapper: Mapping[Any, Any],
    cls: type[Symbol | Scalar | Vector],
):
    if self.expression is None:
        return mapper.get(self, self)
    out = substitute(self.expression, mapper)
    if not isinstance(out, Expression):
        return out
    return cls(name=self.name, namespace=self.namespace, expression=out)


@substitute.register
def substitute_symbol(self: Symbol, mapper: Mapping[Any, Any]) -> Symbol:
    return _substitute_named_expression(self, mapper, self.__class__)


@substitute.register
def substitute_scalar(self: Scalar, mapper: Mapping[Any, Any]) -> Scalar:
    out = _substitute_named_expression(self, mapper, Scalar)
    return cast(Scalar, out)


@substitute.register
def substitute_vector(self: Vector, mapper: Mapping[Any, Any]) -> Vector:
    out = _substitute_named_expression(self, mapper, Vector)
    return cast(Vector, out)


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
