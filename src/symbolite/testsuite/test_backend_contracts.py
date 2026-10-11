"""Vector and Boolean capabilities must preserve meaning across execution paths."""

import types

import pytest

from symbolite import Real, Symbol, Vector, substitute, translate, vector
from symbolite.abstract import Boolean, boolean
from symbolite.core import Unsupported
from symbolite.core.function import Function, Operator
from symbolite.core.lang import Assign, Block
from symbolite.core.symbolite_object import get_symbolite_info
from symbolite.impl import get_all_implementations, libstd
from symbolite.ops import as_code, yield_named
from symbolite.ops.traversal import project

BACKENDS = get_all_implementations()
NUMERICAL = {name: lib for name, lib in BACKENDS.items() if name != "libsympy"}
VECTOR_OPERATIONS = {
    "eq",
    "ne",
    "getitem",
    "add",
    "sub",
    "mul",
    "matmul",
    "truediv",
    "floordiv",
    "neg",
    "pos",
    "invert",
    "sum",
    "prod",
}
BOOLEAN_OPERATIONS = {"and_", "or_", "xor"}
SYMPY_VECTOR_OPERATIONS = {"getitem", "sum", "prod"}


@pytest.fixture(scope="module")
def np():
    return pytest.importorskip("numpy")


def _both(expression, inputs, libsl):
    out = Symbol("out")
    block = Block(tuple(inputs), (out,), (Assign(out, expression),))
    direct = translate(substitute(expression, inputs), libsl)
    compiled = translate(block, libsl)(*inputs.values())
    return direct, compiled


@pytest.mark.parametrize("libsl", BACKENDS.values(), ids=BACKENDS.keys())
@pytest.mark.parametrize(
    "abstract,operations,constructor",
    [(vector, VECTOR_OPERATIONS, "Vector"), (boolean, BOOLEAN_OPERATIONS, "Boolean")],
)
def test_declared_backend_capability_contract(libsl, abstract, operations, constructor):
    namespace = abstract.__name__.rsplit(".", 1)[-1]
    declared = {
        get_symbolite_info(value).name
        for value in vars(abstract).values()
        if isinstance(value, (Function, Operator))
        and get_symbolite_info(value).namespace == namespace
    }
    assert declared == operations
    concrete = getattr(libsl, namespace)
    for name in operations:
        capability = getattr(concrete, name)  # A missing binding must fail.
        unsupported = (
            libsl.__name__.endswith("libsympy")
            and namespace == "vector"
            and name not in SYMPY_VECTOR_OPERATIONS
        )
        if unsupported:
            assert capability is Unsupported
        else:
            assert capability is not Unsupported and callable(capability)
    if libsl.__name__.endswith("libsympy"):
        assert callable(getattr(concrete, constructor))
    else:
        assert getattr(concrete, constructor) is Unsupported


VECTOR_CASES = [
    ("add", lambda v: v + 2, (3, 4, 5)),
    ("sub", lambda v: v - 1, (0, 1, 2)),
    ("mul", lambda v: v * 2, (2, 4, 6)),
    ("matmul", lambda v: v @ v, 14),
    ("truediv", lambda v: v / 2, (0.5, 1.0, 1.5)),
    ("floordiv", lambda v: v // 2, (0, 1, 1)),
    ("neg", lambda v: -v, (-1, -2, -3)),
    ("pos", lambda v: +v, (1, 2, 3)),
    ("invert", lambda v: ~v, (-2, -3, -4)),
    ("eq", lambda v: v.eq(2), (False, True, False)),
    ("ne", lambda v: v.ne(2), (True, False, True)),
    ("getitem", lambda v: v[-1], 3),
    ("sum", vector.sum, 6),
    ("prod", vector.prod, 6),
    ("reflected-add", lambda v: 2 + v, (3, 4, 5)),
    ("reflected-sub", lambda v: 1 - v, (0, -1, -2)),
    ("reflected-mul", lambda v: 2 * v, (2, 4, 6)),
    ("reflected-matmul", lambda v: v.__rmatmul__(v + 1), 20),
    ("reflected-truediv", lambda v: 12 / v, (12, 6, 4)),
    ("reflected-floordiv", lambda v: 5 // v, (5, 2, 1)),
    ("negative-floordiv", lambda v: -v // 2, (-1, -1, -2)),
    ("self-equality", lambda v: v.eq(v), (True, True, True)),
    ("distinct-sum", lambda v: vector.sum(v + 1), 9),
    ("distinct-product", lambda v: vector.prod(v + 1), 24),
]


def test_vector_semantic_cases_cover_every_declared_operation():
    assert VECTOR_OPERATIONS <= {name for name, _, _ in VECTOR_CASES}


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
@pytest.mark.parametrize(
    "name,build,expected", VECTOR_CASES, ids=[v[0] for v in VECTOR_CASES]
)
def test_numerical_vector_contract(np, libsl, name, build, expected):
    if libsl.__name__.endswith("libjax"):
        import jax.numpy as jnp

        values = jnp.asarray((1, 2, 3))
    else:
        values = np.asarray((1, 2, 3))
    v = Vector("v")
    for actual in _both(build(v), {v: values}, libsl):
        np.testing.assert_array_equal(actual, expected)
        assert np.shape(actual) == np.shape(expected)
        if np.shape(expected):
            if libsl.__name__.endswith("libjax"):
                import jax

                assert isinstance(actual, jax.Array)
            else:
                assert isinstance(actual, np.ndarray)
        if np.asarray(expected).dtype.kind == "b":
            assert np.asarray(actual).dtype.kind == "b"


@pytest.mark.parametrize("libsl", BACKENDS.values(), ids=BACKENDS.keys())
@pytest.mark.parametrize("values", [(), [], (2, 3, 4), [2, 3, 4]])
@pytest.mark.parametrize("operation", [vector.sum, vector.prod])
def test_finite_sequence_reduction_contract(libsl, values, operation):
    expected = (
        (0 if operation is vector.sum else 1)
        if not values
        else (9 if operation is vector.sum else 24)
    )
    v = Vector("v")
    expression = operation(v)
    assert translate(substitute(expression, {v: values}), libsl) == expected
    if not libsl.__name__.endswith("libsympy"):
        for actual in _both(expression, {v: values}, libsl):
            assert actual == expected


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
@pytest.mark.parametrize("values", [(1, 2, 3), [1, 2, 3]])
def test_sequence_indexing_contract(libsl, values):
    v = Vector("v")
    assert _both(v[-1], {v: values}, libsl) == (3, 3)
    with pytest.raises(IndexError):
        translate(substitute(v[3], {v: values}), libsl)
    out = Real("out")
    block = Block((v,), (out,), (Assign(out, v[3]),))
    with pytest.raises(IndexError):
        translate(block, libsl)(values)


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
def test_native_array_index_bounds_follow_backend_semantics(np, libsl):
    v, out = Vector("v"), Real("out")
    values = np.asarray([1, 2, 3])
    if libsl.__name__.endswith("libjax"):
        import jax.numpy as jnp

        values = jnp.asarray(values)
        # Native JAX retrieval clamps out-of-bounds indices.
        assert _both(v[5], {v: values}, libsl) == (3, 3)
    else:
        with pytest.raises(IndexError):
            translate(substitute(v[5], {v: values}), libsl)
        block = Block((v,), (out,), (Assign(out, v[5]),))
        with pytest.raises(IndexError):
            translate(block, libsl)(values)


TRUTH_TABLE = [
    (False, False, False, False, False),
    (False, True, False, True, True),
    (True, False, False, True, True),
    (True, True, True, True, False),
]


@pytest.mark.parametrize("libsl", BACKENDS.values(), ids=BACKENDS.keys())
@pytest.mark.parametrize("left,right,and_result,or_result,xor_result", TRUTH_TABLE)
def test_boolean_scalar_truth_tables(
    libsl, left, right, and_result, or_result, xor_result
):
    a, b = Boolean("a"), Boolean("b")
    for expression, expected in (
        (a & b, and_result),
        (a | b, or_result),
        (a ^ b, xor_result),
        (True & a, left),
        (False | a, left),
        (True ^ a, not left),
    ):
        inputs = {a: left, b: right}
        direct = translate(substitute(expression, inputs), libsl)
        assert bool(direct) is expected
        if libsl.__name__.endswith("libsympy"):
            import sympy as sy

            assert direct is (sy.true if expected else sy.false)
            out = Boolean("out")
            block = translate(Block((a, b), (out,), (Assign(out, expression),)), libsl)
            condition = block.body.args[0].rhs
            replacements = {translate(a, libsl): left, translate(b, libsl): right}
            assert bool(condition.subs(replacements)) is expected
        else:
            for actual in _both(expression, inputs, libsl):
                assert bool(actual) is expected
                if libsl is libstd:
                    assert isinstance(actual, bool)
                else:
                    assert actual.dtype.kind == "b" and actual.shape == ()


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
def test_boolean_masks_and_broadcasting(np, libsl):
    a, b = Boolean("a"), Boolean("b")
    left = np.asarray([True, False, True])
    right = np.asarray([False, False, True])
    if libsl.__name__.endswith("libjax"):
        import jax.numpy as jnp

        left, right = jnp.asarray(left), jnp.asarray(right)
    for expression, values, expected in (
        (a & b, {a: left, b: right}, [False, False, True]),
        (a | b, {a: left, b: right}, [True, False, True]),
        (a ^ b, {a: left, b: right}, [True, False, False]),
        (a & b, {a: left, b: True}, [True, False, True]),
    ):
        for actual in _both(expression, values, libsl):
            np.testing.assert_array_equal(actual, expected)
            assert np.shape(actual) == (3,)
            assert np.asarray(actual).dtype.kind == "b"


@pytest.mark.parametrize(
    "operation", sorted(VECTOR_OPERATIONS - {"getitem", "sum", "prod"})
)
def test_std_sequence_arithmetic_is_explicitly_rejected(operation):
    v = Vector("v")
    primitive = getattr(vector, operation)
    expression = (
        primitive(v) if operation in {"neg", "pos", "invert"} else primitive(v, v)
    )
    values = [1, 2, 3]
    with pytest.raises(TypeError, match="Python lists and tuples"):
        translate(substitute(expression, {v: values}), libstd)
    out = Symbol("out")
    block = Block((v,), (out,), (Assign(out, expression),))
    with pytest.raises(TypeError, match="Python lists and tuples"):
        translate(block, libstd)(values)


@pytest.mark.parametrize("libsl", NUMERICAL.values(), ids=NUMERICAL.keys())
def test_invalid_array_inputs_have_matching_native_errors(np, libsl):
    v, w = Vector("v"), Vector("w")
    out = Symbol("out")
    floats = np.asarray([1.5, 2.5])
    left, right = np.asarray([1, 2, 3]), np.asarray([1, 2])
    if libsl.__name__.endswith("libjax"):
        import jax.numpy as jnp

        floats, left, right = map(jnp.asarray, (floats, left, right))
    shape_error = TypeError if libsl.__name__.endswith("libjax") else ValueError
    for expression, values, error in (
        (~v, {v: floats}, TypeError),
        (v + w, {v: left, w: right}, shape_error),
    ):
        with pytest.raises(error):
            translate(substitute(expression, values), libsl)
        block = Block(tuple(values), (out,), (Assign(out, expression),))
        with pytest.raises(error):
            translate(block, libsl)(*values.values())


@pytest.mark.skipif("libsympy" not in BACKENDS, reason="Requires SymPy")
def test_sympy_compound_conditions_preserve_dependencies_and_substitution():
    libsl = BACKENDS["libsympy"]
    x = Real("x")
    condition = (x < 0) & (x > -1)
    result = translate(condition, libsl)
    sx = translate(x, libsl)
    assert result.free_symbols == {sx}
    for value, expected in ((-0.5, True), (-2, False), (0, False), (-1, False)):
        assert bool(result.subs(sx, value)) is expected
        assert bool(translate(substitute(condition, {x: value}), libsl)) is expected


@pytest.mark.skipif("libsympy" not in BACKENDS, reason="Requires SymPy")
@pytest.mark.parametrize(
    "operation", sorted(VECTOR_OPERATIONS - SYMPY_VECTOR_OPERATIONS)
)
def test_sympy_whole_vector_operations_are_unsupported(operation):
    libsl = BACKENDS["libsympy"]
    v, out = Vector("v"), Symbol("out")
    primitive = getattr(vector, operation)
    expression = (
        primitive(v) if operation in {"neg", "pos", "invert"} else primitive(v, v)
    )
    for obj in (expression, Block((v,), (out,), (Assign(out, expression),))):
        with pytest.raises(Unsupported, match=f"vector.{operation}.*libsympy"):
            translate(obj, libsl)


@pytest.mark.skipif("libsympy" not in BACKENDS, reason="Requires SymPy")
@pytest.mark.parametrize("operation", [vector.sum, vector.prod])
def test_sympy_reductions_require_explicit_finite_values(operation):
    libsl = BACKENDS["libsympy"]
    name = get_symbolite_info(operation).name
    with pytest.raises(Unsupported, match=f"vector.{name}.*finite.*libsympy"):
        translate(operation(Vector("v")), libsl)
    x = Real("x")
    result = translate(operation((x, 2)), libsl)
    assert result.subs(translate(x, libsl), 3) == (5 if operation is vector.sum else 6)


@pytest.mark.parametrize(
    "namespace,operation", [("vector", "sub"), ("boolean", "and_")]
)
@pytest.mark.parametrize("binding", [None, Unsupported])
def test_compilation_checks_missing_and_unsupported_capabilities(
    monkeypatch, namespace, operation, binding
):
    module = getattr(libstd, namespace)
    v, flag, out = Vector("v"), Boolean("flag"), Symbol("out")
    expression = v - 1 if namespace == "vector" else flag & True
    input_value = v if namespace == "vector" else flag
    if binding is None:
        monkeypatch.delattr(module, operation)
    else:
        monkeypatch.setattr(module, operation, binding)

    def unexpected_compile(*args, **kwargs):
        pytest.fail("Unsupported primitive reached compilation")

    monkeypatch.setattr(libstd.lang, "compile_code", unexpected_compile)
    block = Block((input_value,), (out,), (Assign(out, expression),))
    with pytest.raises(Unsupported, match=f"{namespace}.{operation}.*libstd"):
        translate(block, libstd)


def test_compiled_capability_validation_preserves_translation_pruning():
    class Opaque:
        pass

    @yield_named.register(Opaque)
    def dependencies_opaque(value):
        yield from ()

    @project.register(Opaque)
    def project_opaque(value):
        raise AssertionError("An overridden subtree must not be inspected")

    @translate.register(Opaque)
    def translate_opaque(value, libsl):
        return "7"

    out = Symbol("out")
    block = Block((), (out,), (Assign(out, Opaque()),))
    assert translate(block, libstd)() == 7


def test_scalar_compilation_does_not_require_an_unused_boolean_namespace():
    backend = types.ModuleType("partial_backend")
    for name in ("real", "symbol", "vector", "lang"):
        setattr(backend, name, getattr(libstd, name))
    x, out = Real("x"), Real("out")
    block = Block((x,), (out,), (Assign(out, x + 1),))
    assert translate(block, backend)(2) == 3
    flag = Boolean("flag")
    block = Block((flag,), (out,), (Assign(out, flag & True),))
    with pytest.raises(Unsupported, match="boolean.and_.*partial_backend"):
        translate(block, backend)


def test_generated_vector_and_boolean_calls_keep_indexed_targets_valid(np):
    v, out = Vector("v"), Vector("out")
    block = Block((v, out), (out,), (Assign(out[0], vector.sum(v - 1)),))
    output = np.zeros(1)
    function = translate(block, libstd)
    assert function(np.asarray([1, 2, 3]), output) is output
    np.testing.assert_array_equal(output, [3])
    assert "out[0] = vector.sum(vector.sub(v, 1))" in function.__symbolite_def__
    assert as_code(Boolean("a") & Boolean("b")) == "boolean.and_(a, b)"


@pytest.mark.skipif("libjax" not in BACKENDS, reason="Requires JAX")
def test_jax_traced_vector_boolean_and_sequence_reduction_contracts(np):
    import jax
    import jax.numpy as jnp

    libsl = BACKENDS["libjax"]
    v, total, flag = Vector("v"), Real("total"), Boolean("flag")
    expression = vector.sum(v - 1)
    block = Block((v,), (total,), (Assign(total, expression),))
    function = jax.jit(translate(block, libsl))
    assert function(jnp.asarray([1, 2, 3])) == 3
    block = Block((v,), (total,), (Assign(total, vector.sum(v)),))
    assert jax.jit(translate(block, libsl))((1, 2, 3)) == 6
    assert jax.jit(translate(block, libsl))(()) == 0
    condition = v.eq(2) | v.eq(3)
    block = Block((v,), (flag,), (Assign(flag, condition),))
    np.testing.assert_array_equal(
        jax.jit(translate(block, libsl))(jnp.asarray([1, 2, 3])),
        [False, True, True],
    )
