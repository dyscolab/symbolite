"""
symbolite.core.ops.as_function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yields all named structures inside a symbolic structure.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from collections.abc import Callable
from functools import singledispatch
from typing import Any


@singledispatch
def as_function(
    obj: Any,
    libsl: types.ModuleType | None = None,
) -> Callable[..., Any]:
    """Converts the expression to a callable function.

    Parameters
    ----------
    obj
        symbolic expression.
    libsl
        implementation module.
    """
    from ..ops import as_function_def
    from .base import compile

    function_def = as_function_def(obj)
    lm = compile(function_def, libsl)

    f = lm["f"]
    f.__symbolite_def__ = function_def
    return f
