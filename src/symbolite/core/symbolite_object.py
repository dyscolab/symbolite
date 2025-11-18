"""
symbolite.core.symbolite_object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides basic funtionality for all symbolic objects.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from functools import singledispatch
from typing import Any, NamedTuple, Self, cast


class SymboliteObject[R: NamedTuple]:
    """Base class for all Symbolite objects.

    Symbolite information is stored in the __symbolite_info__ attributed
    using a NamedTuple specific for each type of symbolic object.
    In this way we make objects opaque
    """

    __symbolite_info__: R

    def __eq__(self, other: object) -> bool:
        if self.__class__ is not other.__class__:
            return False
        other_named = cast(Self, other)
        return get_symbolite_info(self) == get_symbolite_info(other_named)

    def __hash__(self) -> int:
        return hash(get_symbolite_info(self))

    def __str__(self) -> str:
        return self.__class__.__name__ + "#" + str(get_symbolite_info(self))

    def __repr__(self) -> str:
        return self.__class__.__name__ + "#" + repr(get_symbolite_info(self))

    def __set_name__(self, owner: Any, name: str):
        if name.endswith("__return"):
            return

        set_name(self, owner, name)


def get_symbolite_info[R: NamedTuple](obj: SymboliteObject[R]) -> R:
    return obj.__symbolite_info__


def set_symbolite_info[R: NamedTuple](obj: SymboliteObject[R], info: R):
    object.__setattr__(obj, "__symbolite_info__", info)


@singledispatch
def set_name(obj: Any, owner: Any, name: str):
    """Sets the name of a symbolic object when assigned as an attribute.

    This is called automatically by Python when an object is assigned
    as an attribute of a class or instance.
    """
    return
