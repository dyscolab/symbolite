"""
symbolite.ops._tree_view
~~~~~~~~~~~~~~~~~~~~~~~~

Visualize symbolic structures.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import sys
from collections.abc import Iterator
from functools import singledispatch
from typing import Any, Protocol, TypeVar, cast

from ..core import Value
from ..core.call import CallInfo
from ..core.function import Function, FunctionInfo, Operator, OperatorInfo, UserFunction
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.value import Name
from ..ops._get_name import get_full_name
from ._dispatch import TraversalDispatch
from ._traversal import Layer, pairs, project

_T_contra = TypeVar("_T_contra", contravariant=True)


class SupportsWrite(Protocol[_T_contra]):
    def write(self, s: _T_contra, /) -> object: ...


class Printer:
    file: SupportsWrite[str]
    indent_level: int = 0
    indent_width: int
    _current_line: list[str]

    def __init__(
        self, file: SupportsWrite[str] | None = None, indent_width: int = 2
    ) -> None:
        self.file = file or sys.stdout
        self.indent_width = indent_width
        self._current_line = []

    def append(self, value: str):
        self._current_line.append(value)

    def flush_line(self):
        self.file.write(
            " " * self.indent_width * self.indent_level
            + "".join(self._current_line)
            + "\n"
        )
        self._current_line = []

    def indent(self):
        self.flush_line()
        self.indent_level += 1

    def dedent(self):
        self.flush_line()
        self.indent_level -= 1

    def __del__(self):
        try:
            if self._current_line:
                self.flush_line()
        except (OSError, ValueError):
            # A supplied stream may already have been closed during cleanup.
            pass


@singledispatch
def tree_view(obj: Any, pretty_printer: Printer | None = None):
    """Print a structural tree without recursing through expression nodes.

    Custom project adapters are visible in the output. Registered tree_view
    handlers take precedence and can delegate to the saved parent handler.
    With a supplied Printer, the final line remains pending for composition.
    """
    printer = pretty_printer if pretty_printer is not None else Printer()
    stack: list[tuple[int | None, Iterator[tuple[str, Any]]]] = [
        (None, iter((("node", obj),)))
    ]
    active: set[int] = set()
    root = True
    while stack:
        identity, commands = stack[-1]
        try:
            action, value = next(commands)
        except StopIteration:
            stack.pop()
            if identity is not None:
                active.remove(identity)
            continue

        if action == "node":
            if id(value) in active:
                raise ValueError(
                    f"Cycle detected while printing {type(value).__name__}."
                )
            selected = _dispatch.select(value, root=root)
            root = False
            if selected is not None:
                _dispatch.invoke(value, selected, printer)
                continue
            layer = project(value)
            active.add(id(value))
            stack.append((id(value), _commands(value, layer)))
        elif action == "append":
            printer.append(value)
        elif action == "indent":
            printer.indent()
        elif action == "dedent":
            printer.dedent()
        elif action == "flush":
            printer.flush_line()

    if pretty_printer is None:
        printer.flush_line()


def _items(
    children: tuple[Any, ...], labels: tuple[str, ...] = ()
) -> Iterator[tuple[str, Any]]:
    for index, child in enumerate(children):
        if labels:
            yield "append", labels[index]
        yield "node", child
        if index < len(children) - 1:
            yield "append", ","
            yield "flush", None


def _commands(node: Any, layer: Layer) -> Iterator[tuple[str, Any]]:
    labels: tuple[str, ...] = ()
    if isinstance(node, (FunctionInfo, OperatorInfo)):
        yield "append", f"{node.namespace}.{node.name}"
    elif layer.kind == "atom":
        name = get_symbolite_info(node).value if isinstance(node, Value) else None
        if isinstance(name, Name):
            yield "append", get_full_name(name)
        elif isinstance(node, (Function, Operator)):
            info = get_symbolite_info(cast(SymboliteObject[Any], node))
            yield "append", f"{info.namespace}.{info.name}"
        elif isinstance(node, UserFunction):
            yield "append", str(get_symbolite_info(node))
        else:
            yield "append", str(node)
    elif layer.kind == "value":
        yield "append", f"{type(node).__name__}#"
        yield "node", layer.children[0]
    elif layer.kind == "call":
        info = get_symbolite_info(node) if isinstance(node, SymboliteObject) else node
        yield "node", layer.children[0]
        yield "append", "("
        yield "indent", None
        labels = ("",) * len(info.args) + tuple(
            f"{key} = " for key, _ in info.kwargs_items
        )
        yield from _items(layer.children[1:], labels)
        yield "dedent", None
        yield "append", ")"
    else:
        match layer.kind:
            case "tuple":
                opening, closing = "(", ")"
            case "list":
                opening, closing = "[", "]"
            case "dict":
                opening, closing = "{", "}"
            case "object" | "record":
                info_type = (
                    type(get_symbolite_info(node))
                    if layer.kind == "object"
                    else layer.data
                )
                opening, closing = f"{type(node).__name__}(", ")"
                labels = tuple(f"{name} = " for name in info_type._fields)
            case _:
                opening, closing = f"{type(node).__name__}(", ")"
        yield "append", opening
        if layer.children:
            yield "indent", None
            if layer.kind == "dict":
                entries = pairs(layer.children)
                for index, (key, value) in enumerate(entries):
                    yield "node", key
                    yield "append", ": "
                    yield "node", value
                    if index < len(entries) - 1:
                        yield "append", ","
                        yield "flush", None
            else:
                yield from _items(layer.children, labels)
            yield "dedent", None
        yield "append", closing


for _type in (SymboliteObject, Value, CallInfo, FunctionInfo, OperatorInfo):
    tree_view.register(_type, tree_view.dispatch(object))

_dispatch = TraversalDispatch(tree_view, metadata_exclusions=(Value,))
