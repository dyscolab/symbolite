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
    """Execute trusted Python source and return the resulting namespace.

    This uses ordinary Python capabilities and is not a sandbox. Symbolite's
    Python emitter validates identifiers, but arbitrary source and custom code
    implementations must still be trusted by the caller.
    """

    if libsl is None:
        libsl = find_module_in_stack()
    if libsl is None:
        warnings.warn("No libsl provided, defaulting to Python standard library.")
        from . import libstd as libsl

    assert libsl is not None

    backend_namespaces = {
        "symbol": libsl.symbol,
        "real": libsl.real,
        "vector": libsl.vector,
    }
    if hasattr(libsl, "boolean"):
        backend_namespaces["boolean"] = libsl.boolean

    namespace: dict[str, Any] = {}
    exec(  # noqa: S102
        code,
        {
            **backend_namespaces,
            **globals(),
        },
        namespace,
    )
    return namespace


__all__ = ["compile"]
