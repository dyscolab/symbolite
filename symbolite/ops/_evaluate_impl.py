"""
symbolite.core.ops.evaluate_impl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from functools import singledispatch
from operator import attrgetter
from typing import Any

from symbolite.core.expression import NamedExpression

from ..abstract import Real, Symbol, Vector
from ..core import (
    Expression,
    Function,
    SymbolicNamespace,
    SymbolicNamespaceMeta,
    Unsupported,
)
from ..core.function import UserFunction


@singledispatch
def evaluate_impl(expr: Any, libsl: types.ModuleType) -> Any:
    """Evaluate expression.

    Parameters
    ----------
    expr
        symbolic expression.
    libsl
        implementation module.
    """
    return expr


@evaluate_impl.register
def evaluate_impl_str(expr: str, libsl: types.ModuleType) -> Any:  # | Unsupported:
    return attrgetter(expr)(libsl)


def _evaluate_symbol_like(self: Symbol | Real | Vector, libsl: types.ModuleType) -> Any:
    if self.expression is not None:
        return evaluate_impl(self.expression, libsl)

    if self.namespace:
        name = str(self)
        value = evaluate_impl(name, libsl)

        if value is Unsupported:
            raise Unsupported(f"{name} is not supported in module {libsl.__name__}")

        return value

    # User defined symbol, try to map the class
    name = f"{self.__class__.__module__.split('.')[-1]}.{self.__class__.__name__}"
    f = evaluate_impl(name, libsl)

    if f is Unsupported:
        raise Unsupported(f"{name} is not supported in module {libsl.__name__}")

    return f(self.name)


@evaluate_impl.register
def _(self: Symbol, libsl: types.ModuleType) -> Any:
    return _evaluate_symbol_like(self, libsl)


@evaluate_impl.register
def _(self: Real, libsl: types.ModuleType) -> Any:
    return _evaluate_symbol_like(self, libsl)


@evaluate_impl.register
def _(self: Vector, libsl: types.ModuleType) -> Any:
    return _evaluate_symbol_like(self, libsl)


@evaluate_impl.register
def _(expr: Function, libsl: types.ModuleType) -> Any | Unsupported:
    return attrgetter(str(expr))(libsl)


@evaluate_impl.register(SymbolicNamespaceMeta)
@evaluate_impl.register(SymbolicNamespace)
def _(self, libsl: types.ModuleType) -> Any:
    assert isinstance(self, (SymbolicNamespace, SymbolicNamespaceMeta))
    return {
        attr_name: evaluate_impl(getattr(self, attr_name), libsl)
        for attr_name in dir(self)
        if not attr_name.startswith("__")
    }


@evaluate_impl.register
def _(self: Expression, libsl: types.ModuleType) -> Any:
    func = evaluate_impl(self.func, libsl)
    args = tuple(evaluate_impl(arg, libsl) for arg in self.args)
    kwargs = {k: evaluate_impl(arg, libsl) for k, arg in self.kwargs_items}

    try:
        return func(*args, **kwargs)
    except Exception as ex:
        try:
            ex.add_note(f"While evaluating {func}(*{args}, **{kwargs}): {ex}")
        except AttributeError:
            pass
        raise ex


@evaluate_impl.register
def _(obj: UserFunction, libsl: types.ModuleType) -> Any:
    impls = obj._impls
    if libsl in impls:
        return impls[libsl]
    elif "default" in impls:
        return impls["default"]
    else:
        raise Exception(
            f"No implementation found for {libsl.__name__} and no default implementation provided for function {obj!s}"
        )


@evaluate_impl.register
def _(obj: NamedExpression, libsl: types.ModuleType) -> str:
    if obj.expression is None:
        raise
    return evaluate_impl(obj.expression, libsl)
