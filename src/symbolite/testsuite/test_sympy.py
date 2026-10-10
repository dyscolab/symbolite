"""Exercise the public SymPy backend, independently of dynamic discovery."""

import pytest

try:
    import sympy as sy
except ModuleNotFoundError as error:
    if error.name != "sympy":
        raise
    pytest.skip("SymPy is not installed", allow_module_level=True)

from sympy.codegen.ast import (
    Assignment,
    CodeBlock,
    FunctionDefinition,
    Return,
    real,
    untyped,
)

from symbolite import Real, Symbol, Vector, substitute, translate
from symbolite.core.lang import Assign, Block
from symbolite.core.value import Value
from symbolite.impl import Kind, get_all_implementations, libsympy


def _compile_block(block: FunctionDefinition):
    namespace = {}
    # Execute only trusted ASTs constructed within these tests.
    exec(sy.pycode(block), namespace)  # noqa: S102
    return namespace[str(block.name)]


def test_sympy_backend_import_and_discovery():
    assert libsympy.KIND is Kind.VALUE
    assert get_all_implementations()["libsympy"] is libsympy


def test_public_sympy_expression_and_substitution():
    x, y = Real("x"), Real("y")
    sx, sy_ = sy.symbols("x y", real=True)
    expression = x + 2 * y
    assert translate(expression, libsympy) == sx + 2 * sy_
    assert translate(substitute(expression, {x: 3, y: 4}), libsympy) == 11


@pytest.mark.parametrize("cls", [Real, Symbol, Value])
def test_named_statement_values_use_the_same_symbols_as_expressions(cls):
    x, out = cls("x"), cls("out")
    translated_x = translate(x, libsympy)
    translated_out = translate(out, libsympy)
    result = translate(Assign(out, x), libsympy)
    assert result == Assignment(translated_out, translated_x)
    block = translate(Block((x,), (out,), (Assign(out, x),), name="copy"), libsympy)
    assert block.parameters[0].symbol == translated_x
    assert block.parameters[0].type == (real if cls is Real else untyped)
    assert block.body == CodeBlock(result, Return(translated_out))
    assert _compile_block(block)(3) == 3


def test_sympy_tuple_arity_and_nested_containers():
    x = Real("x")
    sx = sy.Symbol("x", real=True)
    assert translate((), libsympy) == sy.Tuple()
    assert translate((x,), libsympy) == sy.Tuple(sx)
    assert translate((x, (x, 2)), libsympy) == sy.Tuple(sx, sy.Tuple(sx, 2))
    expression = {"values": [x + 1, (x, 2)], x: {"inner": x}}
    assert translate(expression, libsympy) == {
        "values": [sx + 1, sy.Tuple(sx, 2)],
        sx: {"inner": sx},
    }
    assert translate(substitute(expression, {x: 3}), libsympy) == {
        "values": [4, sy.Tuple(3, 2)],
        3: {"inner": 3},
    }


def test_sympy_assignment_preserves_symbol_assumptions_and_indexed_targets():
    x, out = Real("x"), Real("out")
    sx, sout = sy.symbols("x out", real=True)
    assert translate(Assign(out, x + 1), libsympy) == Assignment(sout, sx + 1)
    v = Vector("v")
    # SymPy requires a shape for an indexed assignment target.
    sv = sy.IndexedBase("v", shape=(3,))
    assignment = substitute(Assign(v[0], x), {v: sv})
    assert translate(assignment, libsympy) == Assignment(sv[0], sx)


def test_sympy_block_translates_wrappers_and_preserves_statement_order():
    x, total, doubled = map(Real, ("x", "total", "doubled"))
    block = Block(
        (x,),
        (doubled, total),
        (Assign(total, x + 1), Assign(doubled, 2 * total)),
        name="calculate",
    )
    result = translate(block, libsympy)
    sx, stotal, sdoubled = sy.symbols("x total doubled", real=True)
    assert isinstance(result, FunctionDefinition)
    assert str(result.name) == "calculate"
    assert tuple(parameter.symbol for parameter in result.parameters) == (sx,)
    assert result.body == CodeBlock(
        Assignment(stotal, sx + 1),
        Assignment(sdoubled, 2 * stotal),
        Return(sy.Tuple(sdoubled, stotal)),
    )
    assert result.body.args[0].rhs.subs(sx, 3) == 4
    assert _compile_block(result)(3) == (8, 4)


@pytest.mark.parametrize("output_count", [0, 1, 2])
def test_sympy_empty_blocks_support_zero_single_and_repeated_outputs(output_count):
    x = Real("x")
    sx = sy.Symbol("x", real=True)
    block = Block((x,), (x,) * output_count, ())
    result = translate(block, libsympy)
    expected = (
        None if output_count == 0 else sx if output_count == 1 else sy.Tuple(sx, sx)
    )
    assert str(result.name) == "__symbolite_block"
    assert result.body == CodeBlock(Return(expected))
    assert _compile_block(result)(3) == (
        None if output_count == 0 else 3 if output_count == 1 else (3, 3)
    )


def test_sympy_block_without_inputs_or_outputs():
    result = translate(Block((), (), ()), libsympy)
    assert result.parameters == sy.Tuple()
    assert result.body == CodeBlock(Return(None))
    assert _compile_block(result)() is None


def test_sympy_statement_subclasses_use_wrapper_metadata():
    class CustomAssign(Assign):
        pass

    class CustomBlock(Block):
        pass

    x, out = Real("x"), Real("out")
    assignment = CustomAssign(out, x + 1)
    block = CustomBlock((x,), (out,), (assignment,), name="custom")
    result = translate(block, libsympy)
    assert result.body.args[0] == translate(assignment, libsympy)
    assert str(result.name) == "custom"


def test_sympy_statement_preflight_rejects_mutated_dependencies(monkeypatch):
    x, out = Real("x"), Real("out")
    values = [x]
    block = Block((x,), (out,), (Assign(out, values),))
    values.append(Real("missing"))

    def unexpected_backend_call(*args):
        pytest.fail("Invalid Block reached the SymPy backend")

    monkeypatch.setattr(libsympy.lang, "Block", unexpected_backend_call)
    with pytest.raises(ValueError, match="Block line 1.*'missing'"):
        translate(block, libsympy)


def test_sympy_container_children_are_translated_once(monkeypatch):
    seen = []
    previous = libsympy.lang.to_int

    def to_int(value, libsl):
        seen.append(value)
        return previous(value, libsl)

    monkeypatch.setattr(libsympy.lang, "to_int", to_int)
    assert translate([1, (2,), {3: 4}], libsympy) == [1, sy.Tuple(2), {3: 4}]
    assert seen == [1, 2, 3, 4]
