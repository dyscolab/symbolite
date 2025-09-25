"""
symbolite.core.function
~~~~~~~~~~~~~~~~~~~~~~~

Symbolic functions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Generic, TypeVar, cast

from .expression import Expression, NamedExpression
from .named import Named


R = TypeVar("R", bound=NamedExpression)

@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class Function(Named, Generic[R]):
    """A callable primitive that will return a call."""

    fmt: str | None = None
    arity: int | None = None

    @property
    def output_type(self) -> type[R]:
        return cast(type[R], NamedExpression)

    def _call(self, *args: Any, **kwargs: Any) -> R:
        resolver = self._build_resolver(*args, **kwargs)
        return cast(R, self.output_type(expression=resolver))

    def _build_resolver(self, *args: Any, **kwargs: Any) -> Expression[R]:
        if self.arity is None:
            return Expression(self, args, tuple(kwargs.items()))
        if kwargs:
            raise ValueError(
                "If arity is given, keyword arguments should not be provided."
            )
        if len(args) != self.arity:
            raise ValueError(
                f"Invalid number of arguments ({len(args)}), expected {self.arity}."
            )
        return Expression(self, args)

    def format(self, *args: Any, **kwargs: Any) -> str:
        if self.fmt:
            return self.fmt.format(*args, **kwargs)

        plain_args = args + tuple(f"{k}={v}" for k, v in kwargs.items())
        return f"{str(self)}({', '.join((str(v) for v in plain_args))})"
