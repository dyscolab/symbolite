"""Tree printing through structural adapters and iterative descent."""

from dataclasses import dataclass
from io import StringIO
from typing import Any

import pytest

from symbolite import Real, UserFunction
from symbolite.ops import tree_view
from symbolite.ops._tree_view import Printer
from symbolite.ops.traversal import Layer, project


def render(obj, *, indent_width=2):
    output = StringIO()
    printer = Printer(output, indent_width=indent_width)
    tree_view(obj, printer)
    printer.flush_line()
    return output.getvalue()


def test_expression_layout_remains_compatible():
    assert render(Real("x") + 3) == "Real#real.add(\n  x,\n  3\n)\n"
    func = UserFunction.from_function(lambda **kwargs: None)
    text = render(func(first=Real("x"), last=2))
    assert "first = x,\n  last = 2\n)\n" in text


def test_default_printer_flushes_final_line(capsys):
    tree_view(Real("x") + 3)
    assert capsys.readouterr().out == "Real#real.add(\n  x,\n  3\n)\n"


def test_container_and_extension_structure_is_visible():
    @dataclass(frozen=True)
    class Box:
        value: Any

    @project.register(Box)
    def project_box(obj):
        return Layer("box", None, (obj.value,))

    assert render({"entry": [Box(Real("x")), ()]}) == (
        "{\n  entry: [\n    Box(\n      x\n    ),\n    ()\n  ]\n}\n"
    )


def test_deep_expression_and_container_printing_uses_explicit_stacks():
    expr = Real("x")
    for _ in range(2500):
        expr = expr + 1
    # Zero indentation keeps this depth check's output linear in size.
    text = render(expr, indent_width=0)
    assert text.count("Real#real.add(") == 2500
    assert "x,\n" in text
    obj = Real("x")
    for _ in range(2500):
        obj = [obj]
    text = render(obj, indent_width=0)
    assert text.count("[") == text.count("]") == 2500


def test_cycles_fail_and_shared_subtrees_print_per_occurrence():
    cycle = []
    cycle.append(cycle)
    with pytest.raises(ValueError, match="Cycle detected"):
        render(cycle)
    shared = Real("x") + 1
    assert render([shared, shared]).count("Real#real.add(") == 2


def test_tree_override_can_delegate_and_cycle_errors_reset():
    parent = tree_view.dispatch(list)
    calls = []

    def override(obj, printer=None):
        calls.append(obj)
        return parent(obj, printer)

    try:
        tree_view.register(list, override)
        assert render([[Real("x")]]) == "[\n  [\n    x\n  ]\n]\n"
        assert len(calls) == 2
        cycle = []
        cycle.append([cycle])
        with pytest.raises(ValueError, match="Cycle detected"):
            render(cycle)
        assert render([Real("x")]) == "[\n  x\n]\n"
    finally:
        tree_view.register(list, parent)


def test_printer_cleanup_tolerates_closed_stream():
    output = StringIO()
    printer = Printer(output)
    printer.append("pending")
    output.close()
    printer.__del__()
