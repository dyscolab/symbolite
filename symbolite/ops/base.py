"""
symbolite.core.operations
~~~~~~~~~~~~~~~~~~~~~~~~~

Common operations to manipulate symbolic expressions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import collections
import types
import warnings
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..abstract import Symbol


def build_function_code(
    name: str,
    parameters: Iterable[str],
    body: Iterable[str],
    return_variables: Iterable[str],
) -> str:
    """Build function code.

    Parameters
    ----------
    name
        Name of the functions.
    parameters
        Name of the parameters.
    body
        Lines in the body of the function.
    return_variables
        Name of the return variables.
    """

    fdef = (
        f"def {name}({', '.join(parameters)}):\n    "
        + "\n    ".join(body)
        + f"\n    return {', '.join(return_variables)}"
    )
    return fdef


def assign(lhs, rhs):
    return f"{lhs} = {rhs}"


def compile(
    code: str,
    libsl: types.ModuleType | None = None,
) -> dict[str, Any]:
    """Compile the code and return the local dictionary.

    Parameters
    ----------
    expr
        symbolic expression.
    libsl
        implementation module.
    """
    from ..impl import find_module_in_stack

    if libsl is None:
        libsl = find_module_in_stack()
    if libsl is None:
        warnings.warn("No libsl provided, defaulting to Python standard library.")
        from ..impl import libstd as libsl

    assert libsl is not None

    lm: dict[str, Any] = {}
    exec(
        code,
        {
            "symbol": libsl.symbol,
            "real": libsl.real,
            "vector": libsl.vector,
            **globals(),
        },
        lm,
    )
    return lm


def inspect(expr: Any) -> dict[Any, int]:
    """Inspect an expression and return what is there
    and how many times.

    Parameters
    ----------
    expr
        symbolic expression.
    """
    from . import yield_named

    cnt = collections.Counter[Any](yield_named(expr))
    if cnt:
        return dict(cnt)
    return {expr: 1}


def evaluate(expr: Any, libsl: types.ModuleType | None = None) -> Any:
    """Evaluate expression.

    Parameters
    ----------
    expr
        symbolic expression.
    libsl
        implementation module.
    """
    from ..impl import find_module_in_stack
    from . import evaluate_impl

    if libsl is None:
        libsl = find_module_in_stack()
    if libsl is None:
        warnings.warn("No libsl provided, defaulting to Python standard library.")
        from ..impl import libstd as libsl

    return evaluate_impl(expr, libsl)


def is_free_symbol(obj: Any) -> bool:
    from ..abstract import Real, Symbol, Vector

    return (
        isinstance(obj, (Symbol, Real, Vector))
        and obj.expression is None
        and obj.namespace == ""
    )


def free_symbols(obj: Any) -> tuple[Symbol]:
    from . import yield_named

    seen = []
    for el in filter(is_free_symbol, yield_named(obj)):
        if el not in seen:
            seen.append(el)

    return tuple(seen)


def symbol_namespaces(self: Any) -> set[str]:
    """Return a set of symbol libraries"""
    from . import yield_named

    return set(map(lambda s: s.namespace, yield_named(self, False)))


def symbol_names(self: Any, namespace: str | None = "") -> set[str]:
    """Return a set of symbol names (with full namespace indication).

    Parameters
    ----------
    namespace: str or None
        If None, all symbols will be returned independently of the namespace.
        If a string, will compare Symbol.namespace to that.
        Defaults to "" which is the namespace for user defined symbols.
    """
    from . import yield_named
    from .util import compare_namespace

    ff = compare_namespace(namespace)
    return set(map(str, filter(ff, yield_named(self, False))))
