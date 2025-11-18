import itertools
import sys
from functools import singledispatch
from typing import Any, Protocol, TypeVar

from ..core import Value
from ..core.call import CallInfo
from ..core.function import FunctionInfo, OperatorInfo
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.value import Name
from ..ops._get_name import get_name

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
        self.flush_line()


def _default_printer() -> Printer:
    return Printer()


@singledispatch
def tree_view(obj: Any, pretty_printer: Printer | None = None):
    pretty_printer = pretty_printer or _default_printer()
    pretty_printer.append(str(obj))


@tree_view.register(SymboliteObject)
def tree_view_symbolite_object(
    obj: SymboliteObject[Any], pretty_printer: Printer | None = None
):
    pretty_printer = pretty_printer or _default_printer()
    info = get_symbolite_info(obj)
    tree_view(info, pretty_printer)


@tree_view.register(FunctionInfo | OperatorInfo)
def tree_view_function(
    obj: FunctionInfo[Any] | OperatorInfo[Any], pretty_printer: Printer | None = None
):
    pretty_printer = pretty_printer or _default_printer()
    pretty_printer.append(f"{obj.namespace}.{obj.name}")


@tree_view.register
def tree_view_call(obj: CallInfo, pretty_printer: Printer | None = None):
    pretty_printer = pretty_printer or _default_printer()
    tree_view(obj.func, pretty_printer)
    pretty_printer.append("(")
    pretty_printer.indent()

    for ndx, (k, v) in enumerate(
        itertools.chain(map(lambda arg: (None, arg), obj.args), obj.kwargs_items)
    ):
        if k is not None:
            pretty_printer.append(f"{k} = ")
        tree_view(v, pretty_printer)
        if ndx < len(obj.args) + len(obj.kwargs_items) - 1:
            pretty_printer.append(",")
            pretty_printer.flush_line()
    pretty_printer.dedent()
    pretty_printer.append(")")


@tree_view.register(Value)
def tree_view_value(obj: Value[Any], pretty_printer: Printer | None = None):
    pretty_printer = pretty_printer or _default_printer()
    info = get_symbolite_info(obj)
    if isinstance(info.value, Name):
        pretty_printer.append(get_name(info.value, qualified=True))
    else:
        pretty_printer.append(f"{obj.__class__.__name__}#")
        tree_view(info.value, pretty_printer)
