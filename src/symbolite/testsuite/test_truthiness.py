import pytest

from symbolite import Real, Symbol, UserFunction, Vector, substitute, translate
from symbolite.abstract import Boolean
from symbolite.core import Value
from symbolite.core.lang import Assign, Block
from symbolite.impl import libstd


@pytest.mark.parametrize("literal", [True, False])
def test_boolean_literal_truth(literal):
    value = Boolean(literal)
    assert bool(value) is literal
    assert ("yes" if value else "no") == ("yes" if literal else "no")
    assert (not value) is (not literal)


@pytest.mark.parametrize(
    "value",
    [
        Value("value"),
        Value(True),
        Value(False),
        Symbol("symbol"),
        Symbol(False),
        Real("real"),
        Real(0),
        Real(1),
        Vector("vector"),
        Vector([]),
    ],
)
def test_non_boolean_values_reject_truth(value):
    with pytest.raises(TypeError, match="translate"):
        bool(value)


@pytest.mark.parametrize(
    "value",
    [
        Boolean("flag"),
        Boolean(0),
        Boolean(1),
        Boolean(None),
        Boolean([]),
        Boolean([True]),
        Boolean(Boolean(False)),
        Boolean(Value(True)),
    ],
)
def test_boolean_requires_direct_python_bool(value):
    with pytest.raises(TypeError, match="translate"):
        bool(value)


@pytest.mark.parametrize("cls", [Real, Symbol])
@pytest.mark.parametrize(
    "condition",
    [
        pytest.param(lambda x: bool(x < 0), id="bool"),
        pytest.param(lambda x: 1 if x < 0 else 2, id="conditional"),
        pytest.param(lambda x: not (x < 0), id="not"),
        pytest.param(lambda x: (x > 0) and (x < 10), id="and"),
        pytest.param(lambda x: (x < 0) or (x > 10), id="or"),
        pytest.param(lambda x: 0 < x < 10, id="chained-comparison"),
    ],
)
def test_python_conditions_reject_symbolic_truth(cls, condition):
    with pytest.raises(TypeError, match="translate"):
        condition(cls("x"))


@pytest.mark.parametrize("literal", [True, False])
def test_substituting_boolean_literal_allows_truth(literal):
    flag = Boolean("flag")
    assert bool(substitute(flag, {flag: Boolean(literal)})) is literal


@pytest.mark.parametrize("value", [-5, 5])
def test_substitution_does_not_evaluate_comparison(value):
    x = Real("x")
    resolved = substitute(x < 0, {x: value})
    with pytest.raises(TypeError, match="translate"):
        bool(resolved)
    assert bool(translate(resolved, libstd)) is (value < 0)


@pytest.mark.parametrize(
    "expr",
    [Boolean(True) & Boolean(False), Boolean(True) | Boolean(False)],
)
def test_literal_boolean_operations_remain_symbolic(expr):
    with pytest.raises(TypeError, match="translate"):
        bool(expr)


@pytest.mark.parametrize("value,expected", [(-5, False), (5, True), (15, False)])
def test_explicit_conjunction_preserves_both_bounds(value, expected):
    x, result = Real("x"), Boolean("result")
    condition = (0 < x) & (x < 10)
    with pytest.raises(TypeError, match="translate"):
        bool(condition)
    block = Block((x,), (result,), (Assign(result, condition),))
    assert translate(block, libstd)(value) is expected


def test_truth_conversion_does_not_evaluate_user_function():
    calls = []

    def is_negative(value):
        calls.append(value)
        return value < 0

    predicate = UserFunction("is_negative", output_type=Boolean)
    predicate.register_impl(is_negative, libsl=libstd)
    expr = predicate(5)
    with pytest.raises(TypeError, match="translate"):
        bool(expr)
    assert calls == []
    assert translate(expr, libstd) is False
    assert calls == [5]


@pytest.mark.parametrize("cls", [Value, Real, Symbol, Boolean])
def test_structural_equality_and_dictionary_keys_still_work(cls):
    x, same, other = cls("x"), cls("x"), cls("other")
    assert (x == same) is True
    assert (x != same) is False
    assert (x == other) is False
    assert hash(x) == hash(same)
    assert {x: "found"}[same] == "found"
