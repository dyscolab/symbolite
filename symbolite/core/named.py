"""
symbolite.core.named
~~~~~~~~~~~~~~~~~~~~

Provides name, namespace for other objects.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True, repr=False)
class Named:
    name: str | None = None
    namespace: str = ""

    def __str__(self) -> str:
        if self.name is None:
            return "<anonymous>"

        if self.namespace:
            return self.namespace + "." + self.name

        return self.name

    def __repr__(self) -> str:
        from ..ops.util import repr_without_defaults
        return repr_without_defaults(self)

    def format(self, *args: Any, **kwargs: Any) -> str: ...

