"""
symbolite.core.ops.as_function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from functools import singledispatch
from typing import Any, Callable


@singledispatch
def as_function(
    expr: Any,
    libsl: types.ModuleType | None = None,
) -> Callable[..., Any]:
    """Converts the expression to a callable function.

    Parameters
    ----------
    expr
        symbolic expression.
    libsl
        implementation module.
    """
    from ..ops import as_function_def
    from .base import compile

    function_def = as_function_def(expr)
    lm = compile(function_def, libsl)

    f = lm["f"]
    f.__symbolite_def__ = function_def
    return f

