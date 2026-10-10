import types
from collections import UserDict
from typing import Any, assert_type

import pytest

from symbolite import Real, Symbol, real, vector
from symbolite.abstract.boolean import Boolean
from symbolite.abstract.lang import Assign, Block
from symbolite.core import Unsupported
from symbolite.impl import get_all_implementations, libstd
from symbolite.ops import as_code, substitute, translate
from symbolite.ops.base import evaluate, value_names

all_impl = get_all_implementations()

x, y = map(real.Real, ("x", "y"))
vec = vector.Vector("vec")
v = vector.Vector("v")

xsy = Symbol("xsy")

requires_numpy = pytest.mark.skipif("libnumpy" not in all_impl, reason="Requires NumPy")
requires_sympy = pytest.mark.skipif("libsympy" not in all_impl, reason="Requires SymPy")


@pytest.mark.mypy_testing
def test_typing():
    reveal_type(v + v)  # R: symbolite.abstract.vector.Vector # noqa: F821
    reveal_type(2 + v)  # R: symbolite.abstract.vector.Vector # noqa: F821
    reveal_type(v + 2)  # R: symbolite.abstract.vector.Vector # noqa: F821
    reveal_type(vec[0])  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(vec[x])  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(vector.sum(vec))  # R: symbolite.abstract.real.Real # noqa: F821
    assert_type(vector.vectorize(x, order=(x,)), tuple[vector.Vector, Real])
    assert_type(vector.auto_vectorize(x), tuple[vector.Vector, Real])
    assert_type(
        vector.vectorize(xsy, order=(xsy,)), tuple[vector.Vector, Real | Symbol]
    )
    assert_type(vector.auto_vectorize(1), tuple[vector.Vector, int])
    assert_type(vector.vector_inputs(x), tuple[Real | Symbol, ...])
    indices = {x: 3, y: 5}
    assert_type(vector.vectorize(x, indices=indices), tuple[vector.Vector, Real])
    generic_indices = {xsy: 3}
    assert_type(
        vector.vectorize(xsy, indices=generic_indices),
        tuple[vector.Vector, Real | Symbol],
    )
    assert_type(
        vector.vectorize(x + xsy, indices={x: 3, xsy: 5}), tuple[vector.Vector, Real]
    )
    mixed_indices = {x: 3, xsy: 5}
    assert_type(
        vector.vectorize(x + xsy, indices=mixed_indices), tuple[vector.Vector, Real]
    )

    class Scalar(Real):
        pass

    scalar = Scalar("scalar")
    subclass_indices = {scalar: 3}
    assert_type(
        vector.vectorize(scalar, indices=subclass_indices), tuple[vector.Vector, Real]
    )


def test_vector():
    assert as_code(vec) == "vec"
    assert as_code(vec[1]) == "vec[1]"


def test_methods():
    assert substitute(vec, {vec: (1, 2, 3)}) == (1, 2, 3)
    assert evaluate(substitute(vec[1], {vec: (1, 2, 3)})) == 2
    assert value_names(vec) == {
        "vec",
    }
    assert value_names(vec[1]) == {
        "vec",
    }
    assert value_names(vec[1] + vec[0]) == {
        "vec",
    }


@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_impl(libsl: types.ModuleType):
    v = vector.Vector("v")

    v1234 = (1, 2, 3, 4)
    try:
        import numpy as np  # type: ignore

        v1234 = np.asarray(v1234)  # type: ignore
    except ImportError:
        pass

    try:
        expr = vector.sum(v)
        assert evaluate(substitute(expr, {v: v1234}), libsl=libsl) == 10
    except Unsupported:
        pass

    expr = vector.prod(v)
    assert evaluate(substitute(expr, {v: v1234}), libsl=libsl) == 24


@requires_numpy
def test_impl_numpy():
    try:
        import numpy as np  # type: ignore

        from symbolite.impl import libnumpy as libsl
    except ImportError:
        return

    v = np.asarray((1, 2, 3))

    expr1 = vector.Vector("vec") + 1
    assert np.allclose(evaluate(substitute(expr1, {vec: v})), v + 1)

    expr2 = real.cos(vector.sum(vector.Vector("vec")))

    assert np.allclose(
        evaluate(substitute(expr2, {vec: v}), libsl=libsl), np.cos(np.sum(v))
    )


@requires_sympy
def test_impl_sympy():
    try:
        import sympy as sy  # type: ignore

        from symbolite.impl import libsympy as libsl
    except ImportError:
        return

    vec = vector.Vector("vec")
    syarr = sy.IndexedBase("vec")
    assert translate(vec, libsl=libsl) == syarr
    assert translate(vec[1], libsl=libsl) == syarr[1]


@pytest.mark.parametrize(
    "expr,layout,result",
    [
        (x + 2 * y, {"order": (x, y)}, vec[0] + 2 * vec[1]),
        (x + 2 * y, {"order": (y, x)}, vec[1] + 2 * vec[0]),
        (x + 2 * real.cos(y), {"order": (y, x)}, vec[1] + 2 * real.cos(vec[0])),
        (x + 2 * y, {"indices": {x: 3, y: 5}}, vec[3] + 2 * vec[5]),
        (x + 2 * y, {"indices": {x: 5, y: 3}}, vec[5] + 2 * vec[3]),
    ],
)
def test_vectorize(expr: real.Real, layout: Any, result: real.Real):
    target, rewritten = vector.vectorize(expr, into=vec, **layout)
    assert target is vec
    assert rewritten == result


@pytest.mark.parametrize("operation", [vector.vectorize, vector.auto_vectorize])
def test_vectorize_creates_fresh_target(operation):
    kwargs = {"order": (x, y)} if operation is vector.vectorize else {}
    target, rewritten = operation(x + 10 * y, **kwargs)
    other, _ = operation(x + 10 * y, **kwargs)
    assert isinstance(target, vector.Vector)
    assert target is not other
    assert translate(substitute(rewritten, {target: (3, 5)}), libstd) == 53


def test_vectorize_many():
    eqs = [
        x + 2 * y,
        y + 3 * x,
    ]
    result = [
        vec[2] + 2 * vec[0],
        vec[0] + 3 * vec[2],
    ]
    target, rewritten = vector.vectorize(eqs, into=vec, order=(y, Real("z"), x))
    assert target is vec
    assert rewritten == result
    assert isinstance(rewritten, list) and rewritten is not eqs


@pytest.mark.parametrize(
    "expr,result",
    [
        (x + 2 * y, vec[0] + 2 * vec[1]),
        (y + 2 * x, vec[1] + 2 * vec[0]),
        (x + 2 * real.cos(y), vec[0] + 2 * real.cos(vec[1])),
    ],
)
def test_autovectorize(expr: real.Real, result: real.Real):
    target, rewritten = vector.auto_vectorize(expr, into=vec)
    assert target is vec
    assert vector.vector_inputs(expr) == (x, y)
    assert rewritten == result


def test_autovectorize_many():
    eqs = [
        x + 2 * y,
        y + 3 * x,
    ]
    result = [
        vec[0] + 2 * vec[1],
        vec[1] + 3 * vec[0],
    ]
    target, rewritten = vector.auto_vectorize(eqs, into=vec)
    assert target is vec
    assert vector.vector_inputs(eqs) == (x, y)
    assert rewritten == result
    assert isinstance(rewritten, list) and rewritten is not eqs


@pytest.mark.parametrize("mapping_type", [dict, UserDict, types.MappingProxyType])
def test_vectorize_mapping_positions_execute(mapping_type):
    target, rewritten = vector.vectorize(
        x + 10 * y, into=v, indices=mapping_type({x: 3, y: 5})
    )
    values = (1, 2, 0, 3, 0, 5)
    assert target is v
    assert translate(substitute(rewritten, {target: values}), libstd) == 53

    result = Real("result")
    block = Block((target,), (result,), (Assign(result, rewritten),))
    assert translate(block, libstd)(values) == 53


def test_vectorize_partial_layout_and_aliases():
    parameter = Real("parameter")
    target, rewritten = vector.vectorize(
        x + 10 * y + parameter,
        indices={x: 3, y: 3, Real("unused"): 5},
    )
    assert (
        translate(
            substitute(rewritten, {target: (1, 2, 0, 3, 0, 5), parameter: 7}), libstd
        )
        == 40
    )


def test_vectorize_preserves_symbol_types_and_namespaces():
    class Scalar(Real):
        pass

    custom = Scalar("x")
    generic = Symbol("x")
    namespaced = Real("model.x")
    expr = custom + 10 * x + 100 * generic + 1000 * namespaced
    target, rewritten = vector.vectorize(expr, order=(custom, x, generic, namespaced))
    assert translate(substitute(rewritten, {target: (1, 2, 3, 4)}), libstd) == 4321
    assert vector.vector_inputs(custom + x + generic) == (custom, x, generic)


def test_vector_inputs_only_discovers_free_scalars():
    flag = Boolean("flag")
    namespaced = Real("model.x")
    expr = {"values": [y + x + y + real.pi, (vec[0], flag, namespaced)]}
    assert vector.vector_inputs(expr) == (x, y)
    target, rewritten = vector.auto_vectorize(expr)
    assert translate(
        substitute(rewritten["values"][0], {target: (3, 5)}), libstd
    ) == pytest.approx(13 + 3.141592653589793)
    assert rewritten["values"][1] == (vec[0], flag, namespaced)


def test_vector_inputs_equal_names_keep_occurrence_order():
    generic = Symbol("x")
    expr = (generic + x, x + generic, y)
    assert vector.vector_inputs(expr) == (generic, x, y)
    target, rewritten = vector.auto_vectorize(expr)
    assert translate(substitute(rewritten, {target: (3, 5, 7)}), libstd) == (8, 8, 7)


def test_vectorize_nested_containers_and_scalar_leaves():
    expr = {"real": x, "generic": xsy, "nested": [y, (x + y, 7)]}
    target, rewritten = vector.auto_vectorize(expr)
    assert vector.vector_inputs(expr) == (x, xsy, y)
    assert isinstance(rewritten, dict) and rewritten is not expr
    assert (
        isinstance(rewritten["nested"], list)
        and rewritten["nested"] is not expr["nested"]
    )
    assert translate(substitute(rewritten, {target: (3, 5, 7)}), libstd) == {
        "real": 3,
        "generic": 5,
        "nested": [7, (10, 7)],
    }


@pytest.mark.parametrize("expr", [0, 2.5, Real(3), Symbol(4), [], {}, ()])
def test_auto_vectorize_empty_layout(expr):
    assert vector.vector_inputs(expr) == ()
    target, rewritten = vector.auto_vectorize(expr, into=v)
    assert target is v
    assert rewritten == expr
    target, explicit = vector.vectorize(expr, order=())
    assert isinstance(target, vector.Vector)
    assert explicit == expr


@pytest.mark.parametrize("value", [x, xsy])
def test_vectorize_scalar_leaf(value):
    target, rewritten = vector.vectorize(value, order=(value,))
    assert isinstance(rewritten, Real)
    assert translate(substitute(rewritten, {target: (53,)}), libstd) == 53


@pytest.mark.parametrize(
    "kwargs,error,match",
    [
        ({}, ValueError, "exactly one"),
        ({"order": (), "indices": {}}, ValueError, "exactly one"),
        ({"order": (x, x)}, ValueError, "repeated"),
        ({"order": "x"}, TypeError, "sequence"),
        ({"order": iter((x,))}, TypeError, "sequence"),
        ({"order": ("x",)}, TypeError, "named"),
        ({"order": (x + y,)}, TypeError, "named"),
        ({"order": (Real(3),)}, TypeError, "named"),
        ({"order": (vec,)}, TypeError, "named"),
        ({"order": (Boolean("flag"),)}, TypeError, "named"),
        ({"indices": [(x, 3)]}, TypeError, "Mapping"),
        ({"indices": {"x": 3}}, TypeError, "named"),
        ({"indices": {x + y: 3}}, TypeError, "named"),
        ({"indices": {x: -1}}, ValueError, "nonnegative"),
        ({"indices": {x: 1.5}}, TypeError, "integers"),
        ({"indices": {x: True}}, TypeError, "bool"),
        ({"indices": {x: "3"}}, TypeError, "integers"),
        ({"order": (x,), "into": "state"}, TypeError, "into"),
    ],
)
def test_vectorize_rejects_invalid_layouts(kwargs, error, match):
    with pytest.raises(error, match=match):
        vector.vectorize(x + y, **kwargs)


def test_auto_vectorize_rejects_invalid_target():
    with pytest.raises(TypeError, match="into"):
        vector.auto_vectorize(x, into="state")  # type: ignore[call-overload]
