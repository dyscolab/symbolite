import ast
import math

import pytest

from symbolite import Real, Symbol, Vector, real, translate
from symbolite.abstract.boolean import Boolean
from symbolite.core.lang import Assign, Block
from symbolite.impl import get_all_implementations, libstd
from symbolite.impl.libpythoncode._codeexpr import make_attribute, make_function
from symbolite.ops import as_code

NUMERICAL = {
    name: libsl
    for name, libsl in get_all_implementations().items()
    if hasattr(libsl.lang, "CODE_IMPL")
}
NONFINITE = [math.inf, -math.inf, math.nan]


def assert_float_equal(actual, expected):
    if math.isnan(expected):
        assert math.isnan(actual)
    else:
        assert actual == expected
        assert math.copysign(1, actual) == math.copysign(1, expected)


@pytest.mark.parametrize("value", NONFINITE)
@pytest.mark.parametrize("wrap", [lambda value: value, Real, Symbol])
def test_nonfinite_source_is_self_contained(value, wrap):
    code = as_code(wrap(value))
    assert not any(isinstance(node, ast.Name) for node in ast.walk(ast.parse(code)))
    assert_float_equal(eval(code, {"__builtins__": {}}), value)


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
@pytest.mark.parametrize("value", NONFINITE)
def test_compiled_nonfinite_scalar_literals(libsl, value):
    inf, nan, float_name, out = map(Real, ("inf", "nan", "float", "out"))
    block = Block((inf, nan, float_name), (out,), (Assign(out, value),))
    assert_float_equal(translate(block, libsl)(1, 2, 3), value)


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
def test_compiled_nonfinite_structured_literals(libsl):
    out = Symbol("out")
    payload = (math.inf, [-math.inf, {"nan": math.nan}])
    block = Block((), (out,), (Assign(out, payload),))
    result = translate(block, libsl)()
    assert isinstance(result, tuple) and len(result) == 2
    assert isinstance(result[1], list) and len(result[1]) == 2
    assert_float_equal(result[0], math.inf)
    assert_float_equal(result[1][0], -math.inf)
    assert_float_equal(result[1][1]["nan"], math.nan)


@pytest.mark.parametrize(
    "expression,expected",
    [(Real(-math.inf) ** 2, math.inf), (Real(math.nan) * 2, math.nan)],
)
def test_nonfinite_literal_operator_grouping(expression, expected):
    out = Real("out")
    block = Block((), (out,), (Assign(out, expression),))
    assert_float_equal(translate(block, libstd)(), expected)


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
@pytest.mark.parametrize("names", [(), ("x",), ("x", "y"), ("x", "x"), ("y", "x", "y")])
def test_block_output_count_order_and_annotations(libsl, names):
    inputs = Real("x"), Real("y")
    outputs = tuple(Real(name) for name in names)
    function = translate(Block(inputs, outputs, ()), libsl)
    values = {"x": 2, "y": 3}
    expected = tuple(values[name] for name in names)
    if len(names) == 0:
        expected, annotation = None, "None"
    elif len(names) == 1:
        expected, annotation = expected[0], "real.Real"
    else:
        annotation = "tuple[" + ", ".join("real.Real" for _ in names) + "]"
    assert function(2, 3) == expected
    assert function.__annotations__["return"] == annotation


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
def test_repeated_vector_outputs_preserve_aliasing(libsl):
    v = Vector("v")
    function = translate(Block((v,), (v, v), ()), libsl)
    values = [1, 2, 3]
    result = function(values)
    assert isinstance(result, tuple) and len(result) == 2
    assert result[0] is values and result[1] is values


INVALID_NAMES = [
    "class",
    "a b",
    "a;b",
    "a\nb",
    "1x",
    "__debug__",
    "f():\n    pass\nprint('NAME_VALIDATION_PROBE')\ndef g",
]


@pytest.mark.parametrize("name", INVALID_NAMES + ["ns.f"])
def test_invalid_block_names_are_rejected_before_compilation(monkeypatch, capsys, name):
    def unexpected_compile(*args, **kwargs):
        pytest.fail("Invalid declaration reached compilation")

    monkeypatch.setattr(libstd.lang, "compile_code", unexpected_compile)
    block = Block((), (), (), name=name)
    with pytest.raises(ValueError, match="Invalid Python block name"):
        translate(block, libstd)
    with pytest.raises(ValueError, match="Invalid Python block name"):
        as_code(block)
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("cls", [Real, Symbol, Vector, Boolean])
@pytest.mark.parametrize("name", INVALID_NAMES)
def test_invalid_value_names_are_rejected(cls, name):
    value = cls(name)
    with pytest.raises(ValueError, match="Invalid Python"):
        as_code(value)


@pytest.mark.parametrize("position", ["input", "assignment", "output", "rhs"])
def test_invalid_declaration_and_expression_names_are_rejected(monkeypatch, position):
    invalid, out = Real("a;print('NAME_VALIDATION_PROBE')"), Real("out")
    match position:
        case "input":
            block = Block((invalid,), (), ())
        case "assignment":
            block = Block((), (), (Assign(invalid, 1),))
        case "output":
            block = Block((invalid,), (invalid,), ())
        case "rhs":
            block = Block((invalid,), (out,), (Assign(out, invalid + 1),))

    def unexpected_compile(*args, **kwargs):
        pytest.fail("Invalid name reached compilation")

    monkeypatch.setattr(libstd.lang, "compile_code", unexpected_compile)
    with pytest.raises(ValueError, match="Invalid Python"):
        translate(block, libstd)


@pytest.mark.parametrize("factory", [make_function, make_attribute])
@pytest.mark.parametrize("name", ["", "a..b", "class.x", "ns.class", "ns.x;print(1)"])
def test_invalid_qualified_names_are_rejected(factory, name):
    with pytest.raises(ValueError, match="Invalid Python"):
        factory(name)


def test_invalid_keyword_argument_is_rejected():
    function = make_function("f")
    with pytest.raises(ValueError, match="keyword argument"):
        function(**{"x);print(1)": 1})


@pytest.mark.parametrize("inputs", [(Real("x"), Real("x")), (Real("K"), Real("K"))])
def test_duplicate_python_parameter_names_are_rejected(inputs):
    with pytest.raises(ValueError, match="input names must be unique"):
        as_code(Block(inputs, (), ()))


def test_namespaced_block_inputs_are_rejected():
    with pytest.raises(ValueError, match="unqualified named values"):
        as_code(Block((real.pi,), (), ()))


@pytest.mark.parametrize("name", ["_value2", "α", "K"])
def test_valid_unicode_identifiers_and_backend_namespaces(name):
    x, out = Real(name), Real("out")
    block = Block((x,), (out,), (Assign(out, x + real.pi),), name=name)
    function = translate(block, libstd)
    assert function(2) == pytest.approx(2 + math.pi)
    assert as_code(real.pi) == "real.pi"
    assert str(make_function("namespace.f")(1)) == "namespace.f(1)"
