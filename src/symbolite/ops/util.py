"""
symbolite.core.util
~~~~~~~~~~~~~~~~~~~

Symbolite core util functions.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterator, Mapping
from types import ModuleType
from typing import Any

from ._translate import translate
from .base import count_named


def solve_dependencies[TH: Hashable](
    dependencies: Mapping[TH, set[TH]],
) -> Iterator[set[TH]]:
    """Solve a dependency graph.

    Parameters
    ----------
    dependencies :
        dependency dictionary. For each key, the value is an iterable indicating its
        dependencies.

    Yields
    ------
    set
        iterator of sets, each containing keys of independents tasks dependent only of
        the previous tasks in the list.

    Raises
    ------
    ValueError
        if a cyclic dependency is found.
    """
    while dependencies:
        # values not in keys (items without dep)
        t = {i for v in dependencies.values() for i in v} - dependencies.keys()
        # and keys without value (items without dep)
        t.update(k for k, v in dependencies.items() if not v)
        # can be done right away
        if not t:
            raise ValueError(
                "Cyclic dependencies exist among these items: {}".format(
                    ", ".join(repr(x) for x in dependencies.items())
                )
            )
        # and cleaned up
        dependencies = {k: v - t for k, v in dependencies.items() if v}
        yield t


def compute_dependencies[TH: Hashable](
    content: Mapping[TH, Any],
    is_dependency: Callable[[Any], bool],
) -> dict[TH, set[TH]]:
    dependencies: dict[TH, set[TH]] = {}
    for k, v in content.items():
        contents = count_named(v)
        if contents == {k: 1}:
            dependencies[k] = set()
        else:
            dependencies[k] = set(filter(is_dependency, contents.keys()))
    return dependencies


def substitute_content[TH: Hashable](
    content: Mapping[TH, Any],
    *,
    is_dependency: Callable[[Any], bool],
) -> dict[TH, Any]:
    from . import substitute

    dependencies = compute_dependencies(content, is_dependency)
    layers = solve_dependencies(dependencies)
    out: dict[TH, Any] = {}
    for layer in layers:
        for item in layer:
            out[item] = substitute(content[item], out)

    return out


def eval_content[TH: Hashable](
    content: Mapping[TH, Any],
    *,
    libsl: ModuleType,
    is_dependency: Callable[[Any], bool],
) -> dict[TH, Any]:
    """Translate a group of assignments using the given backend.

    Parameters
    ----------
    content
        a mapping of assigments.
    libsl
        symbolite implementation module.
    is_root
        callable that takes a python object/value and returns True
        if it should be considered as having no dependencies.
    is_dependency
        callable that takes a python object/value and returns True
        if it should be considered as the dependency of another.
    """
    from . import substitute

    dependencies = compute_dependencies(content, is_dependency)
    layers = solve_dependencies(dependencies)

    out: dict[TH, Any] = {}
    for layer in layers:
        for item in layer:
            out[item] = translate(substitute(content[item], out), libsl)

    return out
