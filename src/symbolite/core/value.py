"""
symbolite.core.value
~~~~~~~~~~~~~~~~~~~~

Symbolic value.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import random
import string
from typing import Any, NamedTuple

from .call import Call
from .symbolite_object import (
    SymboliteObject,
    get_symbolite_info,
    set_name,
    set_symbolite_info,
)


def id_generator(size: int = 6, chars: str = string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class Name(NamedTuple):
    name: str
    namespace: str


class ValueInfo[PT](NamedTuple):
    # Used to specify the actual value (if any) of the value.
    # - Name
    # - Call: the result of a function call or operations.
    # - PT: python types compatible with this value.
    value: Name | Call | PT


class Value[PT](SymboliteObject[ValueInfo[PT]]):
    """A symbolic value."""

    def __init__(self, name_or_value: Call | Name | PT | str = "") -> None:
        if isinstance(name_or_value, str):
            if not name_or_value:
                name_or_value = Name("__symbolite_var_" + id_generator(), "")
            else:
                parts = name_or_value.split(".")
                if len(parts) == 1:
                    name_or_value = Name(parts[0], "")
                elif len(parts) == 2:
                    name_or_value = Name(parts[1], parts[0])
                else:
                    raise ValueError(
                        f"Invalid value name: expected <name> or <namespace>.<name>, got {name_or_value!r}"
                    )
        set_symbolite_info(self, ValueInfo(name_or_value))


@set_name.register(Value)
def set_name_value(obj: Value[Any], owner: Any, name: str):
    info = get_symbolite_info(obj)

    value = info.value
    if isinstance(value, Name):
        current_name = value.name

        if value.namespace != "":
            return

        if not current_name.startswith("__symbolite_var_") and current_name != name:
            import warnings

            warnings.warn(
                f"Mismatched names in attribute {name}: {type(obj)} is named {current_name}"
            )

        set_symbolite_info(obj, ValueInfo(Name(name, "")))
