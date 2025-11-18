"""
symbolite.impl._lang_value_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runtime helpers for language-level constructs.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import types
import warnings
from typing import Any

from . import find_module_in_stack


def compile(
    code: str,
    libsl: types.ModuleType | None = None,
) -> dict[str, Any]:
    """Compile code for a given implementation module and return the namespace."""

    if libsl is None:
        libsl = find_module_in_stack()
    if libsl is None:
        warnings.warn("No libsl provided, defaulting to Python standard library.")
        from . import libstd as libsl

    assert libsl is not None

    namespace: dict[str, Any] = {}
    exec(
        code,
        {
            "symbol": libsl.symbol,
            "real": libsl.real,
            # "bool": libsl.boolean, # TODO
            "vector": libsl.vector,
            **globals(),
        },
        namespace,
    )
    return namespace


__all__ = ["compile"]
