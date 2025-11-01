"""
symbolite.core.lang
~~~~~~~~~~~~~~~~~~~

Language related primitives.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from typing import Any


class ValueConverter[T]:
    def __call__(self, value: T, libsl: types.ModuleType) -> Any:
        pass
