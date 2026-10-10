import pickle
import types
from copy import copy, deepcopy

import pytest

from symbolite import Symbol, UserFunction, substitute, translate
from symbolite.core.call import Call
from symbolite.core.symbolite_object import get_symbolite_info
from symbolite.impl import get_all_implementations, libstd
from symbolite.ops.base import count_named

all_impl = get_all_implementations()


def f_1_1(x):
    return 2 * x


def f_2_1(x, y):
    return x + y


def f_1_2(x):
    return 1 * x, 2 * x


@pytest.mark.parametrize(
    "func,args,result",
    [
        (f_1_1, (1,), 2),
        (f_2_1, (1, 2), 3),
        (f_1_2, (1,), (1, 2)),
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_user_functions(func, args, result, libsl: types.ModuleType):
    uf = UserFunction.from_function(func)

    output = uf(*args)

    info = get_symbolite_info(output)
    assert isinstance(info.value, Call)
    value_info = get_symbolite_info(info.value)
    assert value_info.func is uf
    assert value_info.args == args
    assert translate(value_info.func, libsl) is func
    assert translate(output, libsl) == result


@pytest.mark.parametrize("clone", [copy, deepcopy], ids=["copy", "deepcopy"])
@pytest.mark.parametrize("with_default", [False, True])
def test_registration_preserves_function_and_expression_keys(clone, with_default):
    func = (
        UserFunction.from_function(f_1_1)
        if with_default
        else UserFunction("f", output_type=Symbol)
    )
    expression = func(Symbol("x"))
    copied_func = clone(func)
    copied_expression = clone(expression)
    function_hash = hash(func)
    expression_hash = hash(expression)
    mapping = {func: "function", expression: "expression"}
    keys = {func, expression}
    counts = count_named((expression, expression))

    for backend in ("default", libstd):
        func.register_impl(f_1_1, backend)

        assert hash(func) == function_hash
        assert hash(expression) == expression_hash
        assert func == copied_func
        assert expression == copied_expression
        assert hash(copied_func) == function_hash
        assert hash(copied_expression) == expression_hash
        assert mapping[func] == mapping[copied_func] == "function"
        assert mapping[expression] == mapping[copied_expression] == "expression"
        assert copied_func in keys
        assert copied_expression in keys
        assert counts[func] == counts[copied_func] == 2


@pytest.mark.parametrize("clone", [copy, deepcopy], ids=["copy", "deepcopy"])
def test_substitution_survives_registration(clone):
    func = UserFunction("f", output_type=Symbol)
    replacement = UserFunction("g", output_type=Symbol)
    x = Symbol("x")
    copied_func = clone(func)
    replacements = {func: replacement}
    expression = func(x)

    func.register_impl(f_1_1, libstd)

    assert substitute(expression, replacements) == replacement(x)
    assert substitute(copied_func(x), replacements) == replacement(x)
    assert substitute({func: [expression]}, replacements) == {
        replacement: [replacement(x)]
    }


@pytest.mark.parametrize("clone", [copy, deepcopy], ids=["copy", "deepcopy"])
def test_function_copies_share_backend_registrations(clone):
    func = UserFunction.from_function(f_1_1)
    copied_func = clone(func)
    copied_expression = copied_func(3)

    func.register_impl(f_1_2, libstd)

    assert translate(func(3), libstd) == (3, 6)
    assert translate(copied_expression, libstd) == (3, 6)
    assert translate(clone(func(3)), libstd) == (3, 6)
    assert get_symbolite_info(func).impls == get_symbolite_info(copied_func).impls

    copied_func.register_impl(f_1_2, "default")
    assert get_symbolite_info(func).impls == get_symbolite_info(copied_func).impls


def test_independent_same_named_user_functions_remain_distinct():
    first = UserFunction("f", output_type=Symbol)
    second = UserFunction("f", output_type=Symbol)
    x = Symbol("x")

    assert first != second
    assert first(x) != second(x)
    assert len({first: 1, second: 2}) == 2

    first.register_impl(f_1_1, libstd)
    second.register_impl(f_1_2, libstd)

    assert first != second
    assert substitute((first(x), second(x)), {first: second}) == (
        second(x),
        second(x),
    )
    assert translate(first(3), libstd) == 6
    assert translate(second(3), libstd) == (3, 6)


def test_user_function_pickle_roundtrip_preserves_identity():
    func = UserFunction.from_function(f_1_1)
    expression = func(3)

    restored_func, restored_expression = pickle.loads(pickle.dumps((func, expression)))

    assert restored_func == func
    assert hash(restored_func) == hash(func)
    assert restored_expression == expression
    assert hash(restored_expression) == hash(expression)
    assert translate(restored_expression, libstd) == 6
