"""
symbolite.core.variable
~~~~~~~~~~~~~~~~~~~~~~~

Symbolic variable.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import random
import string
from typing import Any, NamedTuple

from symbolite.core.symbolite_object import (
    SymboliteObject,
    get_symbolite_info,
    set_name,
    set_symbolite_info,
)

from .call import Call


def id_generator(size: int = 6, chars: str = string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class Name(NamedTuple):
    name: str
    namespace: str


class VariableInfo[PT](NamedTuple):
    # Used to specify the actual value (if any) of the variable.
    # - Name
    # - Call: the result of a function call or operations.
    # - PT: python types compatible with this variable.
    value: Name | Call | PT


class Variable[PT](SymboliteObject[VariableInfo[PT]]):
    """A symbolic variable."""

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
                        f"Invalid variable name: expected <name> or <namespace>.<name>, got {name_or_value!r}"
                    )
        set_symbolite_info(self, VariableInfo(name_or_value))


@set_name.register(Variable)
def set_name_variable(obj: Variable[Any], owner: Any, name: str):
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

        set_symbolite_info(obj, VariableInfo(Name(name, "")))
