from copy import copy, deepcopy

import pytest

from symbolite import Real, Symbol, Vector, real, substitute
from symbolite.abstract.boolean import Boolean
from symbolite.core.symbolite_object import get_symbolite_info
from symbolite.ops import get_name


@pytest.mark.parametrize("cls", [Real, Symbol, Vector, Boolean])
@pytest.mark.parametrize("clone", [copy, deepcopy])
def test_named_descriptor_reuse_preserves_value_and_expression_keys(cls, clone):
    x = cls("x")
    expression = real.sin(x)
    copied_x, copied_expression = clone(x), clone(expression)
    hashes = hash(x), hash(expression)
    mapping = {x: "value", expression: "expression"}
    keys = {x, expression}
    replacements = {x: cls("replacement")}

    with pytest.warns(UserWarning, match="keeping the existing name"):

        class Reuse:
            renamed = x

    assert Reuse.renamed is x
    assert get_name(x) == "x"
    assert (hash(x), hash(expression)) == hashes
    assert x == copied_x == clone(x)
    assert expression == copied_expression == clone(expression)
    assert mapping[copied_x] == mapping[clone(x)] == "value"
    assert mapping[copied_expression] == mapping[clone(expression)] == "expression"
    assert copied_x in keys and copied_expression in keys
    assert substitute(expression, replacements) == real.sin(cls("replacement"))


@pytest.mark.parametrize("cls", [Real, Symbol, Vector, Boolean])
def test_anonymous_descriptor_naming_before_hashing(cls):
    x = cls()

    class Model:
        variable = x
        expression = real.sin(x)

    assert Model.variable is x
    assert get_name(x) == "variable"
    assert Model.expression == real.sin(cls("variable"))
    assert hash(x) == hash(cls("variable"))


@pytest.mark.parametrize("cls", [Real, Symbol, Vector, Boolean])
@pytest.mark.parametrize("key_kind", ["value", "expression"])
def test_anonymous_descriptor_naming_after_hashing_is_rejected(cls, key_kind):
    x = cls()
    key = x if key_kind == "value" else real.sin(x)
    original_info = get_symbolite_info(x)
    original_hash = hash(key)
    mapping = {key: "stored"}

    with pytest.raises((ValueError, RuntimeError)) as exc_info:

        class Reuse:
            renamed = x

    error = (
        exc_info.value
        if isinstance(exc_info.value, ValueError)
        else exc_info.value.__cause__
    )
    assert isinstance(error, ValueError)
    assert "after it has been hashed" in str(error)
    assert get_symbolite_info(x) == original_info
    assert hash(key) == original_hash
    assert mapping[copy(key)] == mapping[deepcopy(key)] == "stored"


def test_matching_and_namespaced_descriptor_aliases_keep_identity():
    x, pi = Real("x"), Real("real.pi")
    named_value = x
    mapping = {x: 1, pi: 2}

    class Model:
        x = copy(named_value)
        constant = pi

    assert Model.x == x
    assert Model.constant is pi
    assert mapping[Model.x] == 1
    assert mapping[Model.constant] == 2
