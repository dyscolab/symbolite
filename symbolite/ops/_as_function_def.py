"""
symbolite.core.ops.as_function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from functools import singledispatch
from typing import Any

from ..core import SymbolicNamespace, SymbolicNamespaceMeta
from ..core.variable import Name, Variable
from .base import assign, build_function_code, free_variables


@singledispatch
def as_function_def(obj: Any) -> str:
    raise TypeError(f"Cannot build function definition for {type(obj)}")


@as_function_def.register(tuple)
@as_function_def.register(list)
def _(
    obj: tuple[Any],
) -> str:
    from ..ops import as_code

    return build_function_code(
        "f",
        map(as_code, free_variables(obj)),
        (assign(f"__return_{ndx}", as_code(el)) for ndx, el in enumerate(obj)),
        map("__return_{}".format, range(len(obj))),
    )


@as_function_def.register(dict)
def _(
    obj: dict[str, Any],
) -> str:
    from ..ops import as_code

    return build_function_code(
        "f",
        map(as_code, free_variables(tuple(obj.values()))),
        ["__return = {}"]
        + [assign(f"__return['{k}']", as_code(el)) for k, el in obj.items()],
        [
            "__return",
        ],
    )


@as_function_def.register(SymbolicNamespaceMeta)
@as_function_def.register(SymbolicNamespace)
def _(
    obj: SymbolicNamespace | SymbolicNamespaceMeta,
) -> str:
    assert isinstance(obj, (SymbolicNamespace, SymbolicNamespaceMeta))

    lines: list[str] = []
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if not isinstance(attr, Variable):
            continue

        if not isinstance(attr.value, Name):
            lines.append(assign(attr_name, f"{attr!s}"))

    return build_function_code(
        obj.__name__,
        map(str, free_variables(obj)),
        lines,
        [
            "__return",
        ],
    )


@as_function_def.register(Variable)
def _(obj: Variable[Any]) -> str:
    from ..ops import as_code

    # info = get_symbolite_info(obj)
    function_name = "f"
    return build_function_code(
        function_name,
        map(as_code, free_variables(obj)),
        [
            assign("__return", as_code(obj)),
        ],
        [
            "__return",
        ],
    )
