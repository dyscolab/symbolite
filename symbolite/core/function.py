"""
symbolite.core.function
~~~~~~~~~~~~~~~~~~~~~~~

Symbolic functions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import dataclasses
import types
from typing import Any, Callable, Literal, Self, cast

from .expression import Expression, NamedExpression
from .named import Named


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class Function[R: NamedExpression](Named):
    """A callable primitive that will return a call."""

    fmt: str | None = None
    arity: int | None = None
    result_cls: type[R]

    def __str__(self) -> str:
        from ..ops import as_string

        return as_string(self)

    @property
    def output_type(self) -> type[R]:
        return cast(type[R], NamedExpression)

    def _call(self, *args: Any, **kwargs: Any) -> R:
        resolver = self._build_resolver(*args, **kwargs)
        return self.result_cls(expression=resolver)

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


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class UnaryFunction[I, R: NamedExpression](Function[R]):
    arity: int = 1

    def __call__(self, arg1: I) -> R:
        return super()._call(arg1)  # type: ignore


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class BinaryFunction[I, R: NamedExpression](Function[R]):
    arity: int = 2

    def __call__(self, arg1: I, arg2: I) -> R:
        return super()._call(arg1, arg2)  # type: ignore


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class Function3[I, R: NamedExpression](Function[R]):
    arity: int = 3

    def __call__(self, arg1: I, arg2: I, arg3: I) -> R:
        return super()._call(arg1, arg2, arg3)  # type: ignore


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class UnaryOperator[I, R: NamedExpression](Function[R]):
    arity: int = 1
    precedence: int

    def __call__(self, arg1: I) -> R:
        return self._call(arg1)


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class BinaryOperator[I, R: NamedExpression](Function[R]):
    arity: int = 2
    precedence: int

    def __call__(self, arg1: I, arg2: I) -> R:
        return self._call(arg1, arg2)


@dataclasses.dataclass(frozen=True, repr=False, kw_only=True)
class UserFunction[P, T, R: NamedExpression](Function[R]):
    _impls: dict[types.ModuleType | Literal["default"], Callable[P, T]] = (
        dataclasses.field(init=False, default_factory=dict)
    )

    @classmethod
    def from_function(cls, func: Callable[P, T]) -> Self:
        obj = cls(
            name=func.__name__,
            namespace="user",
            result_cls=cast(type[R], NamedExpression),
        )
        obj._impls["default"] = func
        return obj

    def __repr__(self) -> str:
        from ..ops.util import repr_without_defaults

        return repr_without_defaults(self, include_private=False)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._call(*args, **kwargs)

    def register_impl(self, func: Callable[P, T], libsl: types.ModuleType):
        self._impls[libsl] = func
