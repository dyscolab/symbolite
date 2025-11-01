"""
symbolite.core.ops._as_code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert a symbolite object to python code.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from functools import singledispatch
from typing import Any

from symbolite.core import SymbolicNamespace, SymbolicNamespaceMeta
from symbolite.core.symbolite_object import get_symbolite_info
from symbolite.core.variable import Name, Variable

from ._get_name import get_name
from .base import free_variables


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


@as_code.register
def _(obj: SymbolicNamespaceMeta | SymbolicNamespace) -> str:
    from ..impl import libpythoncode
    from ._translate import translate

    lines = [f"# {obj.__name__}", ""]

    assign = lambda a, b: f"{a} = {b}"  # noqa: E731

    for free_var in free_variables(obj):
        info = get_symbolite_info(free_var)
        assert isinstance(info.value, Name)
        name = get_name(info.value, qualified=False)
        lines.append(assign(name or "<anonymous>", f"{free_var.__class__.__name__}()"))

    lines.append("")

    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if not isinstance(attr, Variable):
            continue
        info = get_symbolite_info(attr)
        if isinstance(info.value, Name):
            continue
        translated = translate(info.value, libpythoncode)
        lines.append(assign(attr_name, translated))

    return "\n".join(lines)
