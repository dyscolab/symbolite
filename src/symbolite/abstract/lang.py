"""
symbolite.abstract.lang
~~~~~~~~~~~~~~~~~~~~~~~

Language-level symbolic primitives such as assignments and blocks.
"""

from __future__ import annotations

from typing import Any

from ..core.lang import Assign, Block, ValueConverter

to_bool = ValueConverter[bool]()

to_int = ValueConverter[int]()

to_float = ValueConverter[float]()

to_tuple = ValueConverter[tuple[Any, ...]]()

to_list = ValueConverter[list[Any]]()

to_dict = ValueConverter[tuple[tuple[Any, Any], ...]]()


__all__ = [
    "Assign",
    "Block",
    "to_bool",
    "to_int",
    "to_float",
    "to_tuple",
    "to_list",
    "to_dict",
]
