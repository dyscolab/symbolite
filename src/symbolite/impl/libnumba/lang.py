"""
symbolite.impl.libnumba.lang
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Numba-backed implementations for language primitives.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from typing import Any

import numba

from ...abstract.lang import Block as _Block
from ..libnumpy.lang import *
from ..libnumpy.lang import Block as _Block_numpy


def Block(obj: _Block, libsl: Any) -> Any:
    """Translate a BlockInfo into a callable that executes on the target backend."""
    func = _Block_numpy(obj, libsl)
    jit_func = numba.njit(func)
    jit_func.__annotations__ = getattr(func, "__annotations__", {})
    jit_func.__symbolite_def__ = getattr(func, "__symbolite_def__", None)
    jit_func.__symbolite_block__ = getattr(func, "__symbolite_block__", None)
    return jit_func
