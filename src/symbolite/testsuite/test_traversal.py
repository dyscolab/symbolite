"""Structural contracts and independent execution checks for shared traversal."""

import types
from contextvars import copy_context
from dataclasses import dataclass
from typing import Any, NamedTuple

import pytest

from symbolite import Real, Symbol, UserFunction, Vector, real, substitute, translate
from symbolite.abstract.boolean import Boolean
from symbolite.abstract.lang import Assign, Block
from symbolite.core import Call, Unsupported, Value
from symbolite.core.call import CallInfo
from symbolite.core.lang import AssignInfo
from symbolite.core.symbolite_object import SymboliteObject, get_symbolite_info
from symbolite.impl import liblatex, libpythoncode, libstd
from symbolite.impl.libpythoncode._codeexpr import make_function
from symbolite.ops import as_code, count_named, translate_layer, yield_named
from symbolite.ops._traversal import (
    KEEP,
    Layer,
    call_parts,
    fold,
    project,
    rebuild,
    rewrite,
    transform,
    walk,
)
from symbolite.ops.base import free_values, value_names


@pytest.fixture(params=[substitute, rewrite, transform], ids=lambda op: op.__name__)
def no_change_operation(request):
    operation = request.param
    if operation is substitute:
        return lambda obj: substitute(obj, {})
    return lambda obj: operation(obj, lambda node: KEEP)


def test_nested_container_workflow():
    x, y = Real("x"), Real("y")
    expr = {x: [x + 1, (2 * y,)], "other": {y: x - y}}
    changed = substitute(expr, {x: 2, y: 4})
    assert translate(changed, libstd) == {2: [3, (8,)], "other": {4: -2}}
    assert list(expr) == [x, "other"]
    assert free_values(expr) == (x, y)
    assert value_names(expr) == {"x", "y"}
    assert count_named(expr)[x] == 3
    assert count_named(expr)[y] == 3


@pytest.mark.parametrize("container", [tuple, list, dict])
def test_empty_containers_follow_ownership_policy(container, no_change_operation):
    obj = container()
    result = no_change_operation(obj)
    assert result == obj
    if container is tuple:
        assert result is obj
    else:
        assert result is not obj
    assert translate(obj, libstd) == obj
    assert not list(yield_named(obj))


def test_nested_mutable_containers_are_independent_of_inputs(no_change_operation):
    leaf = Real("x") + 1
    untouched = (leaf, 7)
    original = ({"values": [leaf], "empty": {}}, untouched)
    result = no_change_operation(original)
    assert result is not original
    assert result[0] is not original[0]
    assert result[0]["values"] is not original[0]["values"]
    assert result[0]["empty"] is not original[0]["empty"]
    assert result[1] is untouched
    assert result[0]["values"][0] is leaf
    result[0]["values"].append(3)
    result[0]["empty"]["new"] = 4
    result[0]["extra"] = 5
    assert original[0] == {"values": [leaf], "empty": {}}


def test_shared_mutable_containers_are_copied_per_occurrence(no_change_operation):
    leaf = Real("x")
    shared = [leaf]
    original = [shared, shared]
    result = no_change_operation(original)
    assert result is not original
    assert result[0] is not shared and result[1] is not shared
    assert result[0] is not result[1]
    assert result[0][0] is leaf and result[1][0] is leaf
    result[0].append(3)
    assert result[1] == shared == [leaf]


def test_container_copying_propagates_through_symbolic_wrappers(no_change_operation):
    leaf = Real("x")
    payload = {"values": [leaf]}
    original = Value(payload)
    result = no_change_operation(original)
    copied_payload = get_symbolite_info(result).value
    assert type(result) is Value
    assert result is not original
    assert copied_payload is not payload
    assert copied_payload["values"] is not payload["values"]
    assert copied_payload["values"][0] is leaf
    copied_payload["values"].append(3)
    assert payload == {"values": [leaf]}


def test_explicit_replacement_containers_are_returned_as_supplied():
    x = Real("x")
    replacement = {"values": []}
    assert substitute(x, {x: replacement}) is replacement
    assert rewrite(x, lambda node: replacement) is replacement
    assert transform(x, lambda node: replacement) is replacement


@pytest.mark.parametrize("cls", [Real, Symbol, Vector, Boolean, Value])
def test_value_round_trip_preserves_symbolic_class(cls):
    x = Real("x")
    obj = cls(Call(real.add, (x, 1), ()))
    layer = project(obj)
    restored = rebuild(layer, layer.children)
    assert type(restored) is cls
    assert restored == obj
    assert substitute(obj, {}) is obj


def test_changed_value_preserves_subclass_state_without_constructor_call():
    class TaggedValue(Value):
        def __init__(self, value, *, tag):
            super().__init__(value)
            self.tag = tag

    x = Real("x")
    tag = object()
    obj = TaggedValue(Call(real.add, (x, 1), ()), tag=tag)
    changed = substitute(obj, {x: 4})
    assert type(changed) is TaggedValue
    assert changed.tag is tag
    assert translate(changed, libstd) == 5
    assert free_values(obj) == (x,)


def test_simultaneous_leaf_replacement_and_subtree_policy():
    x, y = Real("x"), Real("y")
    assert substitute(x, {x: y, y: 1}) is y
    assert substitute([x, y], {x: y, y: 1}) == [y, 1]
    target = x + 1
    assert substitute(target, {target: 10}) is target
    assert rewrite(target, lambda node: 10 if node is target else KEEP) == 10
    assert substitute(1, {1: None}) is None


def test_unchanged_branches_and_array_ownership():
    np = pytest.importorskip("numpy")
    x, y = Real("x"), Real("y")
    array = np.array([1.0, 2.0])
    untouched = {"array": array, "expression": y + 1}
    expr = [untouched, x + 2]
    changed = substitute(expr, {x: 5})
    assert changed is not expr
    assert changed[0] is not untouched
    assert changed[0]["expression"] is untouched["expression"]
    assert changed[0]["array"] is array
    assert substitute(array, {}) is array
    assert translate(array, libstd) is array
    assert project(array).kind == "atom"
    assert array.tolist() == [1.0, 2.0]
    assert not list(yield_named(array))


def test_dictionary_rewrite_order_and_collisions():
    x, y = Real("x"), Real("y")
    expr = {x: "first", y: "second"}
    changed = substitute(expr, {x: "b", y: "a"})
    assert list(changed.items()) == [("b", "first"), ("a", "second")]
    with pytest.raises(ValueError, match="duplicate dictionary keys"):
        substitute(expr, {x: "same", y: "same"})
    with pytest.raises(TypeError, match="unhashable"):
        substitute(expr, {x: []})
    assert list(expr.items()) == [(x, "first"), (y, "second")]


def test_call_structure_argument_keyword_and_function_order():
    x, y, z = Real("x"), Real("y"), Real("z")
    func = UserFunction.from_function(
        lambda *args, **kwargs: (args, tuple(kwargs.items()))
    )
    call = Call(func, (x, y), {"last": z, "first": x})
    layer = project(call)
    assert layer.children == (func, x, y, z, x)
    restored = rebuild(layer, layer.children)
    assert restored == call
    assert call_parts(layer, layer.children) == (func, (x, y), {"last": z, "first": x})
    assert list(yield_named(call)) == [func, x, y, z, x]
    assert translate(substitute(call, {x: 2, y: 3, z: 4}), libstd) == (
        (2, 3),
        (("last", 4), ("first", 2)),
    )
    assert translate(
        substitute(get_symbolite_info(call), {x: 2, y: 3, z: 4}), libstd
    ) == ((2, 3), (("last", 4), ("first", 2)))


def test_function_replacement():
    x = Real("x")
    assert translate(substitute(real.sin(x), {x: 0, real.sin: real.cos}), libstd) == 1


def test_container_subclasses_are_atomic_without_adapters():
    class ListSubclass(list):
        pass

    class DictSubclass(dict):
        pass

    class Record(NamedTuple):
        value: Any

    x = Real("x")
    for obj in (ListSubclass([x]), DictSubclass(a=x), Record(x)):
        assert project(obj).kind == "atom"
        assert substitute(obj, {x: 1}) is obj
        assert translate(obj, libstd) is obj
        assert not list(yield_named(obj))


def test_structural_extension_and_operation_override_precedence():
    @dataclass(frozen=True)
    class Box:
        value: Any

    @dataclass(frozen=True)
    class BoxLayer(Layer):
        pass

    @project.register(Box)
    def project_box(obj):
        return BoxLayer("box", None, (obj.value,))

    @rebuild.register(BoxLayer)
    def rebuild_box(layer, children):
        return Box(children[0])

    x = Real("x")
    box = Box(x + 1)
    assert substitute(box, {}) is box
    assert free_values(box) == (x,)
    assert translate(substitute([box], {x: 4}), libstd) == [Box(5)]

    @substitute.register(Box)
    def substitute_box(obj, mapper):
        return Box(20)

    @translate.register(Box)
    def translate_box(obj, libsl):
        return 30

    @yield_named.register(Box)
    def named_box(obj):
        yield Real("override")

    assert substitute([box], {x: 4}) == [Box(20)]
    assert translate([box], libstd) == [30]
    assert free_values([box]) == (Real("override"),)


def test_registered_symbolic_subclass_can_delegate_to_parent_handler():
    class CustomValue(Real):
        pass

    parent_substitute = substitute.dispatch(Value)
    parent_translate = translate.dispatch(Value)
    parent_named = yield_named.dispatch(Value)

    @substitute.register(CustomValue)
    def substitute_custom(obj, mapper):
        return parent_substitute(obj, mapper)

    @translate.register(CustomValue)
    def translate_custom(obj, libsl):
        return parent_translate(obj, libsl)

    @yield_named.register(CustomValue)
    def named_custom(obj):
        yield from parent_named(obj)

    x = Real("x")
    obj = CustomValue(Call(real.add, (x, 1), ()))
    assert free_values([obj]) == (x,)
    changed = substitute([obj], {x: 2})
    assert isinstance(changed[0], CustomValue)
    assert translate(changed, libstd) == [3]


def test_override_of_builtin_container_handler_is_used_at_nested_nodes():
    previous = translate.dispatch(tuple)
    try:

        @translate.register(tuple)
        def translate_tuple(obj, libsl):
            return ("override", previous(obj, libsl))

        assert translate([(1, 2)], libstd) == [("override", (1, 2))]
    finally:
        translate.register(tuple, previous)


@pytest.mark.parametrize("container", [tuple, list, dict])
@pytest.mark.parametrize("operation", [substitute, translate, yield_named])
def test_container_overrides_delegate_once_per_occurrence(container, operation):
    x = Real("x")
    obj = {x: x + 1} if container is dict else container([x + 1])
    expr = [obj, obj]
    expected = {2: 3} if container is dict else container([3])
    parent = operation.dispatch(container)
    calls = []

    def override(node, *args):
        calls.append(node)
        return parent(node, *args)

    try:
        operation.register(container, override)
        if operation is substitute:
            result = substitute(expr, {x: 2})
            assert translate(result, libstd) == [expected, expected]
        elif operation is translate:
            assert eval(translate(expr, libpythoncode), {"x": 2}) == [
                expected,
                expected,
            ]
        else:
            named = [x, real.add, x] if container is dict else [real.add, x]
            assert list(yield_named(expr)) == named * 2
        expected_calls = [expr, obj, obj] if container is list else [obj, obj]
        assert len(calls) == len(expected_calls)
        assert all(a is b for a, b in zip(calls, expected_calls, strict=True))
    finally:
        operation.register(container, parent)


def test_broad_wrapper_override_preserves_specific_value_translation():
    previous = translate.dispatch(SymboliteObject)
    try:

        @translate.register(SymboliteObject)
        def translate_wrapper(obj, libsl):
            return "wrapper override"

        assert translate([Real(3), Real(2) + 1], libstd) == [3, "wrapper override"]
    finally:
        translate.register(SymboliteObject, previous)


@pytest.mark.parametrize("operation", [substitute, translate, yield_named])
def test_dispatch_override_can_be_an_unhashable_callable(operation):
    class Leaf:
        pass

    class Handler:
        __hash__ = None

        def __call__(self, obj, *args):
            return iter((Real("override"),)) if operation is yield_named else 7

    operation.register(Leaf, Handler())
    if operation is substitute:
        assert substitute([Leaf()], {}) == [7]
    elif operation is translate:
        assert translate([Leaf()], libstd) == [7]
    else:
        assert list(yield_named([Leaf()])) == [Real("override")]


@pytest.mark.parametrize(
    "operation, wrapper, metadata",
    [(translate, Call, CallInfo), (yield_named, Assign, AssignInfo)],
)
def test_wrapper_override_precedes_metadata_override(operation, wrapper, metadata):
    parent_wrapper = operation.dispatch(wrapper)
    parent_metadata = operation.dispatch(metadata)
    calls = []
    marker = Real("override")

    def override_wrapper(node, *args):
        calls.append("wrapper")
        return iter((marker,)) if operation is yield_named else 7

    def override_metadata(node, *args):
        calls.append("metadata")
        raise AssertionError("Metadata override must be hidden by wrapper override")

    try:
        operation.register(wrapper, override_wrapper)
        operation.register(metadata, override_metadata)
        obj = (
            Call(real.add, (2, 3), ()) if wrapper is Call else Assign(marker, Real("x"))
        )
        if operation is translate:
            assert translate([obj], libstd) == [7]
        else:
            assert list(yield_named([obj])) == [marker]
        assert calls == ["wrapper"]
    finally:
        operation.register(wrapper, parent_wrapper)
        operation.register(metadata, parent_metadata)


def test_registered_call_metadata_handler_is_used_for_wrapped_calls():
    previous = translate.dispatch(CallInfo)
    try:

        @translate.register(CallInfo)
        def translate_info(obj, libsl):
            return previous(obj, libsl) + 10

        assert translate([Real(2) + 3], libstd) == [15]
    finally:
        translate.register(CallInfo, previous)


def test_registered_named_metadata_handler_prunes_wrapped_statement():
    previous = yield_named.dispatch(AssignInfo)
    try:

        @yield_named.register(AssignInfo)
        def named_info(obj):
            yield Real("override")

        statement = Assign(Real("out"), Real("x") + 1)
        assert free_values([statement]) == (Real("override"),)
    finally:
        yield_named.register(AssignInfo, previous)


def test_custom_copy_cannot_mutate_original_wrapper():
    class SameCopy(Value):
        def __copy__(self):
            return self

    x = Real("x")
    obj = SameCopy(Call(real.add, (x, 1), ()))
    with pytest.raises(TypeError, match="copying must return a new wrapper"):
        substitute(obj, {x: 3})
    assert free_values(obj) == (x,)


def test_walk_is_lazy():
    class Bomb:
        pass

    @project.register(Bomb)
    def project_bomb(obj):
        raise AssertionError("Unrequested subtree was visited")

    x = Real("x")
    expr = [x, Bomb()]
    nodes = walk(expr)
    assert next(nodes) is expr
    assert next(nodes) is x
    nodes.close()
    named = yield_named(expr)
    assert next(named) is x
    named.close()


@pytest.mark.parametrize(
    "operation",
    [
        lambda obj: list(walk(obj)),
        lambda obj: fold(obj, lambda layer, children: children),
        lambda obj: rewrite(obj, lambda node: KEEP),
        lambda obj: substitute(obj, {}),
        lambda obj: translate(obj, libstd),
        lambda obj: list(yield_named(obj)),
    ],
)
def test_cycles_fail_without_recursion(operation):
    obj = []
    obj.append({"back": obj})
    with pytest.raises(ValueError, match="Cycle detected"):
        operation(obj)


def test_shared_subtrees_are_visited_and_executed_per_occurrence():
    calls = []

    def next_value():
        calls.append(None)
        return len(calls)

    func = UserFunction.from_function(next_value)
    shared = func()
    expr = real.add(shared, shared)
    assert translate(expr, libstd) == 3
    assert len(calls) == 2
    assert count_named(expr)[func] == 2


def test_deep_expression_uses_explicit_stacks():
    x = Real("x")
    expr = x
    for _ in range(2500):
        expr = expr + 1
    assert substitute(expr, {}) is expr
    assert free_values(expr) == (x,)
    assert count_named(expr)[real.add] == 2500
    changed = substitute(expr, {x: 2})
    assert translate(changed, libstd) == 2502
    assert as_code(changed).startswith("2 + 1 + 1")


def test_nested_literal_containers_generate_executable_code_once():
    x = Real("x")
    expr = {"quoted ' key": [x + 1, "a\n'b", ()], "tuple": ("x", 3)}
    replaced = substitute(expr, {x: 4})
    expected = {"quoted ' key": [5, "a\n'b", ()], "tuple": ("x", 3)}
    assert translate(replaced, libstd) == expected
    assert eval(as_code(replaced)) == expected
    assert as_code("x") == "'x'"


def test_symbol_attribute_uses_literal_name_in_generated_code():
    expr = Symbol("obj").answer
    code = as_code(expr)
    assert eval(code, {"obj": types.SimpleNamespace(answer=42)}) == 42


@pytest.mark.parametrize("backend", [libpythoncode, liblatex])
def test_container_conversion_does_not_translate_children_twice(monkeypatch, backend):
    calls = []
    original = backend.lang.to_int

    def counted(value, libsl):
        calls.append(value)
        return original(value, libsl)

    monkeypatch.setattr(backend.lang, "to_int", counted)
    translate([1, (2,), {3: 4}], backend)
    assert calls == [1, 2, 3, 4]


def test_numerical_user_default_never_executes_during_code_translation():
    calls = []

    def twice(value):
        calls.append(value)
        return 2 * value

    func = UserFunction.from_function(twice)
    for backend in (libpythoncode, liblatex):
        with pytest.raises(Unsupported, match="explicit implementation"):
            translate([func(3)], backend)
    assert calls == []
    assert translate(func(3), libstd) == 6
    func.register_impl(make_function("twice"), libpythoncode)
    assert eval(as_code(func(3)), {"twice": twice}) == 6


def test_unsupported_resolution_raises_before_argument_execution(monkeypatch):
    calls = []
    func = UserFunction.from_function(lambda: calls.append(None))
    monkeypatch.setattr(libstd.real, "erf", Unsupported)
    with pytest.raises(Unsupported, match="real.erf"):
        translate(real.erf(func()), libstd)
    assert calls == []
    monkeypatch.delattr(libstd.real, "erf")
    with pytest.raises(Unsupported, match="real.erf"):
        translate(real.erf(1), libstd)
    with pytest.raises(Unsupported, match="lang.Block"):
        translate(Block((), (), ()), liblatex)


def test_call_failure_keeps_exception_and_context():
    with pytest.raises(ZeroDivisionError) as caught:
        translate(Real(1) / 0, libstd)
    assert any("While translating" in note for note in caught.value.__notes__)


def test_block_handlers_remain_specialized_and_check_dictionary_dependencies():
    x, out, missing = Real("x"), Symbol("out"), Real("missing")
    with pytest.raises(ValueError, match="missing"):
        Block((x,), (out,), (Assign(out, {"value": missing}),))
    block = Block((x,), (out,), (Assign(out, {"value": [x + 1]}),), name="mapping")
    copied = substitute(block, {})
    assert copied is not block
    original_assign = get_symbolite_info(block).lines[0]
    copied_assign = get_symbolite_info(copied).lines[0]
    original_rhs = get_symbolite_info(original_assign).rhs
    copied_rhs = get_symbolite_info(copied_assign).rhs
    assert copied_assign is not original_assign
    assert copied_rhs is not original_rhs
    assert copied_rhs["value"] is not original_rhs["value"]
    assert copied_rhs["value"][0] is original_rhs["value"][0]
    copied_rhs["extra"] = 3
    assert "extra" not in original_rhs
    assert translate(copied, libstd)(4) == {"value": [5], "extra": 3}
    assert translate(block, libstd)(4) == {"value": [5]}
    changed = substitute(block, {x: Real("y")})
    assert translate(changed, libstd)(4) == {"value": [5]}


def test_literal_counts_keep_legacy_hashable_fallback():
    assert count_named(3) == {3: 1}
    assert count_named([1, 2]) == {}
    assert count_named({"a": 3}) == {}


@pytest.mark.parametrize("operation", [substitute, translate, yield_named])
@pytest.mark.parametrize("indirect", [False, True])
def test_delegating_container_overrides_reject_cycles_and_reset(operation, indirect):
    parent = operation.dispatch(list)

    def override(node, *args):
        return parent(node, *args)

    cycle = []
    cycle.append([cycle] if indirect else cycle)
    try:
        operation.register(list, override)
        with pytest.raises(ValueError, match="Cycle detected"):
            if operation is substitute:
                operation(cycle, {})
            elif operation is translate:
                operation(cycle, libstd)
            else:
                list(operation(cycle))
        if operation is substitute:
            assert operation([1], {}) == [1]
        elif operation is translate:
            assert operation([1], libstd) == [1]
        else:
            assert list(operation([Real("x")])) == [Real("x")]
    finally:
        operation.register(list, parent)


def test_named_override_context_does_not_leak_between_generator_yields():
    parent = yield_named.dispatch(list)

    def override(node):
        yield from parent(node)

    obj = [[Real("x"), Real("y")]]
    try:
        yield_named.register(list, override)
        pending = yield_named(obj)
        assert next(pending) == Real("x")
        assert list(yield_named(obj)) == [Real("x"), Real("y")]
        pending.close()
        assert list(yield_named(obj)) == [Real("x"), Real("y")]
    finally:
        yield_named.register(list, parent)


def test_copied_context_does_not_retain_an_expired_override():
    parent = substitute.dispatch(list)
    contexts = []
    child = [1]

    def override(node, mapper):
        if node is child:
            contexts.append(copy_context())
        return parent(node, mapper)

    try:
        substitute.register(list, override)
        result = substitute([child], {})
        assert result[0] == child and result[0] is not child
        resumed = contexts[0].run(substitute, [child], {})
        assert resumed[0] == child and resumed[0] is not child
    finally:
        substitute.register(list, parent)


def test_substitution_projects_custom_nodes_once_per_occurrence():
    @dataclass(frozen=True)
    class Node:
        child: Any

    projections = []

    @project.register(Node)
    def project_node(node):
        projections.append(node)
        return Layer("node", node, (node.child,))

    shared = Node(7)
    obj = Node((shared, shared))
    assert substitute(obj, {}) is obj
    assert len(projections) == 3
    assert projections[0] is obj
    assert projections[1] is shared and projections[2] is shared


def test_transform_sees_transformed_children_and_retains_symbolic_leaves():
    untouched = [Real("x")]
    obj = [[[[1]], untouched]]
    seen = []

    def flatten_numbers(node):
        if isinstance(node, list):
            seen.append(node)
            if len(node) == 1 and isinstance(node[0], int):
                return node[0]
        return KEEP

    changed = transform(obj, flatten_numbers)
    assert changed == [[1, untouched]]
    assert changed[0][1] is not untouched
    assert changed[0][1][0] is untouched[0]
    assert seen[0] == [1]
    assert seen[1] == [1]
    assert transform(obj, lambda node: KEEP) is not obj


def test_transform_is_iterative_and_processes_shared_leaves_per_occurrence():
    marker = object()
    calls = []

    def rule(node):
        if node is marker:
            calls.append(None)
            return len(calls)
        return KEEP

    assert transform((marker, marker), rule) == (1, 2)
    obj = marker
    for _ in range(2500):
        obj = [obj]
    result = transform(obj, lambda node: KEEP)
    original = obj
    for _ in range(2500):
        assert result is not original
        result, original = result[0], original[0]
    assert result is original is marker
    cycle = []
    cycle.append(cycle)
    with pytest.raises(ValueError, match="Cycle detected"):
        transform(cycle, rule)


def test_transform_replacements_are_not_revisited():
    replacement = []
    replacement.append(replacement)
    assert transform(1, lambda node: replacement) is replacement


def test_layer_translation_hook_handles_deep_extensions_and_override_precedence():
    @dataclass(frozen=True)
    class Increment:
        child: Any

    @dataclass(frozen=True)
    class IncrementLayer(Layer):
        pass

    @project.register(Increment)
    def project_increment(node):
        return IncrementLayer("increment", None, (node.child,))

    @translate_layer.register(IncrementLayer)
    def translate_increment(layer, children, libsl):
        return children[0] + 1

    obj = 3
    for _ in range(2500):
        obj = Increment(obj)
    assert translate(obj, libstd) == 2503

    @translate.register(Increment)
    def override(node, libsl):
        return 90

    assert translate([obj], libstd) == [90]


def test_call_diagnostics_preserve_original_error_with_failing_representations():
    class BadRepr:
        def __repr__(self):
            raise TypeError("repr failed")

    error = ValueError("original backend failure")

    def fail(arg):
        raise error

    func = UserFunction.from_function(fail)
    with pytest.raises(ValueError) as caught:
        translate(func(BadRepr()), libstd)
    assert caught.value is error
    assert error.__context__ is None
    assert any("While translating" in note for note in error.__notes__)


def test_call_diagnostics_are_bounded_and_do_not_format_the_exception():
    class BadStrError(Exception):
        def __str__(self):
            raise TypeError("exception formatting failed")

    error = BadStrError()

    def fail(arg):
        raise error

    func = UserFunction.from_function(fail)
    with pytest.raises(BadStrError) as caught:
        translate(func("x" * 10000), libstd)
    assert caught.value is error
    assert len(error.__notes__[0]) < 500


def test_public_traversal_exports_share_the_extension_registry():
    from symbolite.ops import traversal

    assert traversal.project is project
    assert traversal.rebuild is rebuild
    assert traversal.transform is transform
