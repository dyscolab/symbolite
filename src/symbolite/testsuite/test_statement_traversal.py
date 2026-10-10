"""Statement ownership, validation, and iterative substitution contracts."""

import types

import pytest

from symbolite import Real, UserFunction, Vector, substitute, translate
from symbolite.core.lang import Assign, AssignInfo, Block, BlockInfo
from symbolite.core.symbolite_object import get_symbolite_info, set_symbolite_info
from symbolite.impl import libpythoncode, libstd
from symbolite.ops.traversal import KEEP, project, rebuild, rewrite, transform


@pytest.fixture(params=[substitute, rewrite, transform], ids=lambda op: op.__name__)
def unchanged_operation(request):
    operation = request.param
    if operation is substitute:
        return lambda node: substitute(node, {})
    return lambda node: operation(node, lambda child: KEEP)


@pytest.fixture
def tagged_block():
    constructors = []

    class TaggedAssign(Assign):
        def __init__(self, lhs, rhs, *, tag):
            constructors.append("assignment")
            super().__init__(lhs, rhs)
            self.tag = tag

    class TaggedBlock(Block):
        def __init__(self, inputs, outputs, lines, *, tag, name):
            constructors.append("block")
            super().__init__(inputs, outputs, lines, name=name)
            self.tag = tag

    x, out = Real("x"), Real("out")
    assign = TaggedAssign(out, {"values": [x + 1]}, tag=object())
    block = TaggedBlock((x,), (out,), (assign,), tag=object(), name="tagged")
    return block, constructors


@pytest.fixture
def statement_backend():
    backend = types.ModuleType("statement_backend")
    calls = []

    def render_statement(node, libsl):
        assert libsl is backend
        calls.append(node)
        return "statement"

    backend.lang = types.SimpleNamespace(
        Assign=render_statement,
        Block=render_statement,
        to_list=lambda children, libsl: list(children),
    )
    return backend, calls


def test_statement_container_copying_preserves_subclasses_and_state(
    tagged_block, unchanged_operation
):
    original, constructors = tagged_block
    original_info = get_symbolite_info(original)
    original_assign = original_info.lines[0]
    original_rhs = get_symbolite_info(original_assign).rhs
    result = unchanged_operation(original)
    info = get_symbolite_info(result)
    assign = info.lines[0]
    rhs = get_symbolite_info(assign).rhs

    assert type(result) is type(original) and result is not original
    assert type(assign) is type(original_assign) and assign is not original_assign
    assert result.tag is original.tag and assign.tag is original_assign.tag
    assert constructors == ["assignment", "block"]
    assert info.inputs is original_info.inputs
    assert info.outputs is original_info.outputs
    assert rhs is not original_rhs and rhs["values"] is not original_rhs["values"]
    assert rhs["values"][0] is original_rhs["values"][0]
    rhs["values"].append(7)
    assert len(original_rhs["values"]) == 1
    assert translate(original, libstd)(3) == {"values": [4]}


@pytest.mark.parametrize("vectorized", [False, True])
def test_changed_statement_subclasses_keep_state_and_block_interface_policy(
    tagged_block, vectorized
):
    original, constructors = tagged_block
    original_info = get_symbolite_info(original)
    x, out = original_info.inputs[0], original_info.outputs[0]
    replacements = {original_info.name: "must_not_rename_the_block"}
    if vectorized:
        incoming, outgoing, other = (
            Vector("incoming"),
            Vector("outgoing"),
            Vector("other"),
        )
        replacements.update(
            {x: incoming[0], out: outgoing[0], incoming: other, outgoing: other}
        )
        expected_inputs, expected_outputs = (incoming, outgoing), (outgoing,)
    else:
        y, new_out = Real("y"), Real("new_out")
        replacements.update({x: y, out: new_out})
        expected_inputs, expected_outputs = (y,), (new_out,)

    result = substitute(original, replacements)
    info = get_symbolite_info(result)
    original_assign, assign = original_info.lines[0], info.lines[0]
    assert type(result) is type(original) and result.tag is original.tag
    assert type(assign) is type(original_assign) and assign.tag is original_assign.tag
    assert constructors == ["assignment", "block"]
    assert info.name == original_info.name
    assert info.inputs == expected_inputs and info.outputs == expected_outputs
    fn = translate(result, libstd)
    if vectorized:
        output = [None]
        assert fn([3], output) is output
        assert output == [{"values": [4]}]
    else:
        assert fn(3) == {"values": [4]}
    assert get_symbolite_info(original) is original_info


def test_immutable_unchanged_statements_retain_identity(unchanged_operation):
    x, out = Real("x"), Real("out")
    assign = Assign(out, x + 1)
    block = Block((x,), (out,), (assign,), name="unchanged")
    assert unchanged_operation(assign) is assign
    assert unchanged_operation(block) is block


@pytest.mark.parametrize("operation", [rewrite, transform])
def test_structural_changes_reject_undefined_block_dependencies(operation):
    x, out, missing = Real("x"), Real("out"), Real("missing")
    block = Block((x,), (out,), (Assign(out, x + 1),), name="dependency")

    def rule(node):
        return missing if type(node) is int and node == 1 else KEEP

    with pytest.raises(ValueError, match="Block line 1.*'missing'"):
        operation(block, rule)
    assert translate(block, libstd)(2) == 3


@pytest.mark.parametrize("operation", [rewrite, transform])
def test_structural_changes_reject_undefined_block_outputs(operation):
    x, out, missing = Real("x"), Real("out"), Real("missing")
    block = Block((x,), (out,), (Assign(out, x + 1),), name="output")
    original_outputs = get_symbolite_info(block).outputs

    def rule(node):
        return (missing,) if node is original_outputs else KEEP

    with pytest.raises(ValueError, match="Block output value 'missing'"):
        operation(block, rule)
    assert get_symbolite_info(block).outputs is original_outputs


@pytest.mark.parametrize("metadata", [False, True], ids=["wrapper", "record"])
def test_transform_rule_can_repair_block_interface_after_children_change(
    tagged_block, metadata
):
    original, constructors = tagged_block
    original_info = get_symbolite_info(original)
    missing = Real("missing")
    seen = []

    def rule(node):
        if type(node) is int and node == 1:
            return missing
        info = get_symbolite_info(node) if isinstance(node, Block) else node
        if isinstance(info, BlockInfo):
            seen.append(info)
            repaired = info._replace(inputs=info.inputs + (missing,))
            return repaired if metadata else rebuild(project(node), tuple(repaired))
        return KEEP

    result = transform(original_info if metadata else original, rule)
    assert len(seen) == 1
    if metadata:
        assert isinstance(result, BlockInfo)
        result = rebuild(project(original), tuple(result))
    assert type(result) is type(original) and result.tag is original.tag
    assert constructors == ["assignment", "block"]
    assert get_symbolite_info(result).inputs == (*original_info.inputs, missing)
    assert translate(result, libstd)(2, 3) == {"values": [5]}
    assert translate(original, libstd)(2) == {"values": [3]}


def test_transform_does_not_defer_explicit_rebuild_calls_inside_its_rule():
    x, out, missing = Real("x"), Real("out"), Real("missing")
    original = Block((x,), (out,), (Assign(out, x + 1),))
    seen = []

    def rule(node):
        if type(node) is int and node == 1:
            return missing
        if isinstance(node, Block):
            seen.append(node)
            return rebuild(project(node), tuple(get_symbolite_info(node)))
        return KEEP

    with pytest.raises(ValueError, match="Block line 1.*'missing'"):
        transform(original, rule)
    assert len(seen) == 1
    assert translate(original, libstd)(2) == 3


@pytest.mark.parametrize("metadata", [False, True], ids=["wrapper", "record"])
def test_transform_validates_explicit_block_results_after_the_rule(metadata):
    x, out, missing = Real("x"), Real("out"), Real("missing")
    replacement = Block((x,), (out,), (Assign(out, x + 1),))
    invalid = get_symbolite_info(replacement)._replace(lines=(Assign(out, missing),))
    set_symbolite_info(replacement, invalid)
    replacement = invalid if metadata else replacement
    with pytest.raises(ValueError, match="Block line 1.*'missing'"):
        transform(0, lambda node: replacement)


@pytest.mark.parametrize("metadata", [False, True], ids=["wrapper", "record"])
@pytest.mark.parametrize("invalid_output", [False, True])
def test_direct_rebuilding_validates_block_records_and_wrappers(
    metadata, invalid_output
):
    x, out, missing = Real("x"), Real("out"), Real("missing")
    block = Block((x,), (out,), (Assign(out, x + 1),), name="rebuild")
    info = get_symbolite_info(block)
    if invalid_output:
        children = (info.inputs, (missing,), info.lines, info.name)
        message = "Block output value 'missing'"
    else:
        children = (info.inputs, info.outputs, (Assign(out, missing),), info.name)
        message = "Block line 1.*'missing'"
    with pytest.raises(ValueError, match=message):
        rebuild(project(info if metadata else block), children)
    restored = rebuild(project(info if metadata else block), tuple(info))
    if metadata:
        assert isinstance(restored, BlockInfo) and restored == info
    else:
        assert isinstance(restored, Block) and restored is not block
        assert translate(restored, libstd)(2) == 3


@pytest.mark.parametrize("container", [False, True], ids=["direct", "in-list"])
@pytest.mark.parametrize("block_root", [False, True], ids=["assignment", "block"])
def test_deep_assignment_substitution_uses_the_shared_stack(container, block_root):
    out = Real("out")
    original = 0
    for _ in range(2500):
        original = Assign(out, [original] if container else original)
    root = Block((out,), (out,), (original,)) if block_root else original
    if not container:
        assert substitute(root, {}) is root
    changed = substitute(root, {0: 2})
    if block_root:
        assert changed is not root
        changed = get_symbolite_info(changed).lines[0]
    old, new = original, changed
    for _ in range(2500):
        assert type(new) is Assign and new is not old
        old_info, new_info = get_symbolite_info(old), get_symbolite_info(new)
        assert old_info.lhs is new_info.lhs is out
        old, new = old_info.rhs, new_info.rhs
        if container:
            assert new is not old
            old, new = old[0], new[0]
    assert old == 0 and new == 2


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("kind", ["assignment", "assignment-list", "block"])
def test_statement_cycles_raise_diagnostics_and_leave_no_active_state(kind, nested):
    out = Real("out")
    if kind == "assignment":
        cycle = Assign(out, 1)
        set_symbolite_info(cycle, AssignInfo(out, cycle))
    else:
        rhs = []
        assign = Assign(out, rhs)
        cycle = assign if kind == "assignment-list" else Block((), (out,), (assign,))
        rhs.append(cycle)
    with pytest.raises(ValueError, match="Cycle detected"):
        substitute([cycle] if nested else cycle, {})
    valid = Assign(out, [1])
    assert get_symbolite_info(substitute(valid, {1: 2})).rhs == [2]


@pytest.mark.parametrize("base", [Assign, Block])
def test_statement_overrides_can_delegate_to_saved_iterative_parent(base):
    x, out = Real("x"), Real("out")
    assign = Assign(out, [x + 1])
    obj = assign if base is Assign else Block((x,), (out,), (assign,))
    parent = substitute.dispatch(base)
    calls = []

    def override(node, mapper):
        calls.append(node)
        return parent(node, mapper)

    try:
        substitute.register(base, override)
        result = substitute([obj, obj], {})
        assert len(calls) == 2 and all(node is obj for node in calls)
        assert result[0] is not obj and result[1] is not obj
        assert result[0] is not result[1]
    finally:
        substitute.register(base, parent)


def test_statement_substitution_uses_metadata_for_multiple_inheritance():
    class AssignmentFirst(Assign, Block):
        pass

    class BlockFirst(Block, Assign):
        pass

    x, out = Real("x"), Real("out")
    assign = AssignmentFirst(out, [x + 1])
    block = BlockFirst((x,), (out,), (assign,))
    changed = substitute(block, {x: Real("y")})
    assert type(changed) is BlockFirst
    assert type(get_symbolite_info(changed).lines[0]) is AssignmentFirst
    assert translate(changed, libstd)(3) == [4]


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("invalid_output", [False, True])
def test_translation_revalidates_mutable_blocks_before_backend_calls(
    tagged_block, statement_backend, nested, invalid_output
):
    original, _constructors = tagged_block
    result = substitute(original, {})
    info = get_symbolite_info(result)
    missing = Real("missing")
    executions = []
    if invalid_output:
        set_symbolite_info(result, info._replace(outputs=(missing,)))
        message = "Block output value 'missing'"
    else:
        func = UserFunction.from_function(lambda: executions.append(None))
        get_symbolite_info(info.lines[0]).rhs["values"].extend([func(), missing])
        message = "Block line 1.*'missing'"
    backend, calls = statement_backend
    with pytest.raises(ValueError, match=message):
        translate([result] if nested else result, backend)
    assert calls == [] and executions == []
    assert translate(original, backend) == "statement"
    assert len(calls) == 1 and calls[0] is original


@pytest.mark.parametrize("backend", [libstd, libpythoncode])
@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize(
    "kind", ["assignment", "assignment-list", "block", "block-lines"]
)
def test_translation_rejects_statement_cycles_before_backend_recursion(
    backend, nested, kind
):
    out = Real("out")
    if kind == "assignment":
        cycle = Assign(out, 1)
        set_symbolite_info(cycle, AssignInfo(out, cycle))
    elif kind == "block-lines":
        cycle = Block((), (out,), (Assign(out, 1),))
        set_symbolite_info(cycle, get_symbolite_info(cycle)._replace(lines=(cycle,)))
    else:
        rhs = []
        assign = Assign(out, rhs)
        cycle = assign if kind == "assignment-list" else Block((), (out,), (assign,))
        rhs.append(cycle)
    with pytest.raises(ValueError, match="Cycle detected"):
        translate([cycle] if nested else cycle, backend)
    translate(Assign(out, 2), backend)


def test_statement_preflight_is_iterative_and_does_not_evaluate_functions(
    statement_backend,
):
    backend, calls = statement_backend
    executions = []
    func = UserFunction.from_function(lambda: executions.append(None))
    obj = func()
    out = Real("out")
    for _ in range(2500):
        obj = Assign(out, [obj])
    assert translate(obj, backend) == "statement"
    assert executions == []
    assert len(calls) == 1 and calls[0] is obj


def test_statement_preflight_preserves_registered_subtree_pruning():
    class Opaque:
        pass

    @project.register(Opaque)
    def project_opaque(node):
        raise AssertionError("An overridden subtree must not be projected")

    calls = []

    @translate.register(Opaque)
    def translate_opaque(node, libsl):
        calls.append(node)
        return "7"

    rhs = Opaque()
    assert translate(Assign(Real("out"), rhs), libpythoncode) == "out = 7"
    assert len(calls) == 1 and calls[0] is rhs


@pytest.mark.parametrize("base", [Assign, Block])
def test_statement_preflight_checks_saved_parent_delegation(statement_backend, base):
    class CustomStatement(base):
        pass

    parent = translate.dispatch(base)

    @translate.register(CustomStatement)
    def translate_custom(node, libsl):
        return parent(node, libsl)

    out = Real("out")
    if base is Assign:
        cycle = CustomStatement(out, 1)
        set_symbolite_info(cycle, AssignInfo(out, cycle))
    else:
        cycle = CustomStatement((), (out,), (Assign(out, 1),))
        set_symbolite_info(cycle, get_symbolite_info(cycle)._replace(lines=(cycle,)))
    backend, calls = statement_backend
    with pytest.raises(ValueError, match="Cycle detected"):
        translate(cycle, backend)
    assert calls == []


def test_statement_preflight_does_not_cache_mutable_graph_validation(
    tagged_block, statement_backend
):
    original, _constructors = tagged_block
    result = substitute(original, {})
    backend, calls = statement_backend
    assert translate(result, backend) == "statement"
    values = get_symbolite_info(get_symbolite_info(result).lines[0]).rhs["values"]
    values.append(Real("missing"))
    with pytest.raises(ValueError, match="Block line 1.*'missing'"):
        translate(result, backend)
    assert len(calls) == 1
    values.pop()
    assert translate(result, backend) == "statement"
    assert len(calls) == 2 and all(node is result for node in calls)
