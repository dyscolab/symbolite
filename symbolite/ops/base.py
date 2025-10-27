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
from typing import Any, Callable

from ..core.symbolite_object import get_symbolite_info
from ..core.variable import Name, Variable
from ._get_name import get_name, get_namespace


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


def count_named(obj: Any) -> dict[Any, int]:
    """Inspect an expression and return what is there
    and how many times.

    Parameters
    ----------
    obj
        symbolic expression.
    """
    from . import yield_named

    cnt = collections.Counter[Any](yield_named(obj))
    if cnt:
        return dict(cnt)
    return {obj: 1}


def _unwrap_translation(value: Any) -> Any:
    from ..impl.libpythoncode._codeexpr import CodeExpr

    if isinstance(value, CodeExpr):
        return value.text
    if isinstance(value, tuple):
        return tuple(_unwrap_translation(v) for v in value)
    if isinstance(value, list):
        return [_unwrap_translation(v) for v in value]
    if isinstance(value, dict):
        return {k: _unwrap_translation(v) for k, v in value.items()}
    return value


def evaluate(expr: Any, libsl: types.ModuleType | None = None) -> Any:
    """Translate expression into a backend representation.

    Parameters
    ----------
    expr
        symbolic expression.
    libsl
        implementation module.
    """
    from ..impl import Kind, find_module_in_stack
    from ._translate import translate

    if libsl is None:
        libsl = find_module_in_stack()
    if libsl is None:
        warnings.warn("No libsl provided, defaulting to Python standard library.")
        from ..impl import libstd as libsl
    else:
        if libsl.KIND != Kind.VALUE:
            raise ValueError(
                f"Implementation module {libsl} of kind {libsl.KIND} cannot be used for evaluation."
            )

    result = translate(expr, libsl)
    return _unwrap_translation(result)


def is_free_variable(obj: Any) -> bool:
    from ..core.variable import Variable

    if not isinstance(obj, Variable):
        return False

    info = get_symbolite_info(obj)
    return isinstance(info.value, Name) and info.value.namespace == ""


def free_variables(obj: Any) -> tuple[Variable[Any], ...]:
    from . import yield_named

    seen: list[Any] = []
    for el in filter(is_free_variable, yield_named(obj)):
        if el not in seen:
            seen.append(el)

    return tuple(seen)


def symbol_namespaces(self: Any) -> set[str]:
    """Return a set of symbol libraries"""
    from . import yield_named

    return {get_name(s).namespace for s in yield_named(self)}


def compare_namespace(namespace: str) -> Callable[[Any], bool]:
    def _inner(obj: Any) -> bool:
        return get_namespace(obj) == namespace

    return _inner


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

    if namespace is None:
        return set(map(get_name, yield_named(self)))
    else:
        return set(
            map(get_name, filter(compare_namespace(namespace), yield_named(self)))
        )
