"""
symbolite.ops.base
~~~~~~~~~~~~~~~~~~

Common operations to manipulate symbolic expressions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import collections
import types
import warnings
from typing import Any, Callable

from ..core.symbolite_object import get_symbolite_info
from ..core.value import Name, Value
from ._get_name import get_name, get_namespace


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

    return translate(expr, libsl)


def is_free_value(obj: Any) -> bool:
    from ..core.value import Value

    if not isinstance(obj, Value):
        return False

    info = get_symbolite_info(obj)
    return isinstance(info.value, Name) and info.value.namespace == ""


def free_values(obj: Any) -> tuple[Value[Any], ...]:
    from . import yield_named

    seen: list[Any] = []
    for el in filter(is_free_value, yield_named(obj)):
        if el not in seen:
            seen.append(el)

    return tuple(seen)


def compare_namespace(namespace: str) -> Callable[[Any], bool]:
    def _inner(obj: Any) -> bool:
        return get_namespace(obj) == namespace

    return _inner


def value_names(self: Any, namespace: str | None = "") -> set[str]:
    """Return a set of value names (with full namespace indication).

    Parameters
    ----------
    namespace: str or None
        If None, all values will be returned independently of the namespace.
        If a string, will compare valu.namespace to that.
        Defaults to "" which is the namespace for user defined values.
    """
    from . import yield_named

    if namespace is None:
        return set(map(get_name, yield_named(self)))
    else:
        return set(
            map(get_name, filter(compare_namespace(namespace), yield_named(self)))
        )
