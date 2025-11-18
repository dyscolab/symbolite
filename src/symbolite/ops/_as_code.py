"""
symbolite.ops._as_code
~~~~~~~~~~~~~~~~~~~~~~

Convert a symbolite object to python code.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from functools import singledispatch
from typing import Any


@singledispatch
def as_code(obj: Any) -> str:
    """Convert a symbolite object to python code."""
    from ..impl import libpythoncode
    from ._translate import translate

    s = translate(obj, libpythoncode)
    if hasattr(s, "text"):
        return s.text
    elif isinstance(s, str):
        return s
    else:
        return str(s)
