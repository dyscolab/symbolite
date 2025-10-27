"""
symbolite.core.function
~~~~~~~~~~~~~~~~~~~~~~~

Symbolic functions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

import types
from typing import Any, Callable, Literal, NamedTuple, Protocol, Self, cast

from .call import Call
from .symbolite_object import SymboliteObject, get_symbolite_info, set_symbolite_info
from .variable import Variable


class SymbolicCallable[O: Variable[Any]](Protocol):
    """A callable tha returns a symbolic object."""

    def __call__(self, *args: Any, **kwds: Any) -> O: ...


class FunctionInfo[O: Variable[Any]](NamedTuple):
    name: str
    namespace: str
    # Use None to indicate that the arity is unknown or it has keyword arguments
    arity: int | None
    # Result symbolic class
    output_type: type[O]


class Function[O: Variable[Any]](SymboliteObject[FunctionInfo[O]]):
    """A callable primitive that will return a Variable with a Call as value."""

    def __init__(
        self,
        name: str,
        namespace: str = "",
        *,
        arity: int | None = None,
        output_type: type[O],
    ) -> None:
        set_symbolite_info(self, FunctionInfo(name, namespace, arity, output_type))

    def __call__(self, *args: Any, **kwds: Any) -> O:
        info = get_symbolite_info(self)
        if info.arity is None:
            return info.output_type(Call(self, args, kwds))
        if kwds:
            raise ValueError(
                "If arity is given, keyword arguments should not be provided."
            )
        if len(args) != info.arity:
            raise ValueError(
                f"Invalid number of arguments ({len(args)}), expected {info.arity}."
            )

        expr = Call(self, args, tuple())

        return info.output_type(expr)


class UnaryFunction[I, O: Variable[Any]](Function[O]):
    def __init__(self, name: str, namespace: str = "", *, output_type: type[O]) -> None:
        set_symbolite_info(self, FunctionInfo(name, namespace, 1, output_type))

    def __call__(self, arg1: I) -> O:
        return super().__call__(arg1)


class BinaryFunction[I, O: Variable[Any]](Function[O]):
    def __init__(self, name: str, namespace: str = "", *, output_type: type[O]) -> None:
        set_symbolite_info(self, FunctionInfo(name, namespace, 2, output_type))

    def __call__(self, arg1: I, arg2: I) -> O:
        return super().__call__(arg1, arg2)


class Function3[I, O: Variable[Any]](Function[O]):
    def __init__(self, name: str, namespace: str = "", *, output_type: type[O]) -> None:
        set_symbolite_info(self, FunctionInfo(name, namespace, 3, output_type))

    def __call__(self, arg1: I, arg2: I, arg3: I) -> O:
        return super().__call__(arg1, arg2, arg3)


class OperatorInfo[O: Variable[Any]](NamedTuple):
    name: str
    namespace: str
    fmt: str
    arity: int
    output_type: type[O]
    precedence: int


class Operator[O: Variable[Any]](SymboliteObject[OperatorInfo[O]]):
    """A callable primitive that will return a Variable with a Call as value.

    Unlike Function, Operators has a precedence that allow to write it back
    as string in algebraic manner.
    """

    def __init__(
        self,
        name: str,
        namespace: str = "",
        *,
        fmt: str,
        arity: int,
        output_type: type[O],
        precedence: int = 0,
    ) -> None:
        set_symbolite_info(
            self, OperatorInfo(name, namespace, fmt, arity, output_type, precedence)
        )

    def __call__(self, *args: Any, **kwds: Any) -> O:
        info = get_symbolite_info(self)

        if len(args) != info.arity:
            raise ValueError(
                f"Invalid number of arguments ({len(args)}), expected {info.arity}."
            )

        expr = Call(self, args, tuple())

        return info.output_type(expr)


class UnaryOperator[I, O: Variable[Any]](Operator[O]):
    def __init__(
        self,
        name: str,
        namespace: str = "",
        *,
        fmt: str,
        output_type: type[O] = Variable,
        precedence: int = 0,
    ) -> None:
        super().__init__(
            name,
            namespace,
            fmt=fmt,
            arity=1,
            output_type=output_type,
            precedence=precedence,
        )

    def __call__(self, arg1: I) -> O:
        return super().__call__(arg1)


class BinaryOperator[I1, I2, O: Variable[Any]](Operator[O]):
    def __init__(
        self,
        name: str,
        namespace: str = "",
        *,
        fmt: str,
        output_type: type[O] = Variable,
        precedence: int = 0,
    ) -> None:
        super().__init__(
            name,
            namespace,
            fmt=fmt,
            arity=2,
            output_type=output_type,
            precedence=precedence,
        )

    def __call__(self, arg1: I1, arg2: I2) -> O:
        return super().__call__(arg1, arg2)


class UserFunctionInfo[P, T, O: Variable[Any]](NamedTuple):
    name: str
    namespace: str
    # Use None to indicate that the arity is unknown or it has keyword arguments
    arity: int | None
    # Result symbolic class
    output_type: type[O]
    impls: tuple[tuple[types.ModuleType | Literal["default"], Callable[[P], T]], ...]


class UserFunction[P, T, O: Variable[Any]](SymboliteObject[UserFunctionInfo[P, T, O]]):
    def __init__(
        self,
        name: str,
        namespace: str = "",
        *,
        arity: int | None = None,
        output_type: type[O],
    ) -> None:
        set_symbolite_info(
            self, UserFunctionInfo(name, namespace, arity, output_type, ())
        )

    @classmethod
    def from_function(cls, func: Callable[[P], T]) -> Self:
        obj = cls(
            name=func.__name__,
            namespace="",
            output_type=cast(type[O], Variable),
        )
        obj.register_impl(func, libsl="default")
        return obj

    def register_impl(
        self, func: Callable[[P], T], libsl: types.ModuleType | Literal["default"]
    ) -> None:
        info = get_symbolite_info(self)
        info = info._replace(impls=info.impls + ((libsl, func),))
        set_symbolite_info(self, info)

    def __call__(self, *args: Any, **kwds: Any) -> O:
        info = get_symbolite_info(self)
        if info.arity is None:
            return info.output_type(Call(self, args, kwds))
        if kwds:
            raise ValueError(
                "If arity is given, keyword arguments should not be provided."
            )
        if len(args) != info.arity:
            raise ValueError(
                f"Invalid number of arguments ({len(args)}), expected {info.arity}."
            )

        expr = Call(self, args, tuple())

        return info.output_type(expr)
