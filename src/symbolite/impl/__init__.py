"""
symbolite.impl
~~~~~~~~~~~~~~

Concrete implementations for symbolite library

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import importlib
import inspect
import types
from enum import Enum, auto
from pathlib import Path


class Kind(Enum):
    VALUE = auto()
    CODE = auto()


def find_module_in_stack(name: str = "libsl") -> types.ModuleType | None:
    """Find libraries in stack.

    Parameters
    ----------
    expr
        If None, an implementation for every abstract library
        will be look for.
        If an expression, it will be first inspected to find
        which libraries it is using and only those will be look for.

    """
    frame = inspect.currentframe()
    while frame:
        if name in frame.f_locals:
            mod = frame.f_locals[name]
            if mod is not None:
                return mod
        frame = frame.f_back

    return None


def get_all_implementations(
    kind: Kind | tuple[Kind, ...] = Kind.VALUE,
) -> dict[str, types.ModuleType]:
    if not isinstance(kind, tuple):
        kind = (kind,)

    out: dict[str, types.ModuleType] = {}

    path = Path(__file__)
    for p in path.parent.iterdir():
        name = p.stem
        if name.startswith("_"):
            continue

        try:
            module = importlib.import_module(f".{name}", package=__package__)
        except ImportError:
            pass
        else:
            if module.KIND in kind:
                out[name] = module

    return out
