"""
symbolite.core.ops.as_function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from functools import singledispatch
from typing import Any

from ..abstract import Scalar, Symbol, Vector
from ..core import NamedExpression, SymbolicNamespace, SymbolicNamespaceMeta
from .base import assign, build_function_code, free_symbols


@singledispatch
def as_function_def(expr: Any) -> str:
    raise TypeError(f"Cannot build function definition for {type(expr)}")


@as_function_def.register(tuple)
@as_function_def.register(list)
def _(
    expr: tuple[Any],
) -> str:
    return build_function_code(
        "f",
        map(str, free_symbols(expr)),
        (assign(f"__return_{ndx}", str(el)) for ndx, el in enumerate(expr)),
        map("__return_{}".format, range(len(expr))),
    )


@as_function_def.register(dict)
def _(
    expr: dict[str, Any],
) -> str:
    return build_function_code(
        "f",
        map(str, free_symbols(tuple(expr.values()))),
        ["__return = {}"] + [assign(f"__return['{k}']", str(el)) for k, el in expr.items()],
        [
            "__return",
        ],
    )



@as_function_def.register(SymbolicNamespaceMeta)
@as_function_def.register(SymbolicNamespace)
def _(
    expr,
) -> str:
    assert isinstance(expr, (SymbolicNamespace, SymbolicNamespaceMeta))

    lines: list[str] = []
    for attr_name in dir(expr):
        attr = getattr(expr, attr_name)
        if not isinstance(attr, (Symbol, Scalar, Vector)):
            continue

        if attr.expression is not None:
            lines.append(assign(attr_name, f"{attr!s}"))

    return build_function_code(
        expr.__name__,
        map(str, free_symbols(expr)),
        lines,
        [
            "__return",
        ],
    )



@as_function_def.register
def _(expr: NamedExpression) -> str:
    function_name = expr.name or "f"
    return build_function_code(
        function_name,
        map(str, free_symbols(expr)),
        [
            assign("__return", str(expr)),
        ],
        [
            "__return",
        ],
    )
