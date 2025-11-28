"""
symbolite.core.lang
~~~~~~~~~~~~~~~~~~~

Language related primitives.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from typing import Any, NamedTuple

from .value import Value


class ValueConverter[T]:
    def __call__(self, value: T, libsl: types.ModuleType) -> Any:
        return value


class AssignInfo(NamedTuple):
    lhs: Value[Any]
    rhs: Any


class BlockInfo(NamedTuple):
    inputs: tuple[Value[Any], ...]
    outputs: tuple[Value[Any], ...]
    lines: tuple[AssignInfo, ...]
    name: str = ""
