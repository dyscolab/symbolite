"""Backend binding and extension contracts for shared translation handlers."""

import types

import pytest

from symbolite import Real, real, translate
from symbolite.core import Unsupported
from symbolite.core.function import FunctionInfo, OperatorInfo
from symbolite.core.lang import Assign, Block
from symbolite.impl import libpythoncode, libstd


@pytest.fixture
def language_backend():
    backend = types.ModuleType("recording_backend")
    calls = []

    def record(label):
        def convert(obj, libsl):
            assert libsl is backend
            calls.append((label, obj))
            return label

        return convert

    backend.lang = types.SimpleNamespace(
        to_bool=record("boolean"),
        to_int=record("integer"),
        to_float=record("float"),
        to_str=record("string"),
        Assign=record("assignment"),
        Block=record("block"),
        to_list=lambda children, libsl: list(children),
    )
    return backend, calls


def test_language_binding_preserves_subclasses_and_method_resolution(language_backend):
    class Integer(int):
        pass

    class Floating(float):
        pass

    class Text(str):
        pass

    class Statement(Assign):
        pass

    class Program(Block):
        pass

    class AssignmentFirst(Assign, Block):
        pass

    class BlockFirst(Block, Assign):
        pass

    x = Real("x")
    objects = [
        True,
        False,
        Integer(2),
        Floating(1.5),
        Text("literal"),
        Statement(x, x + 1),
        Program((x,), (x,), ()),
        AssignmentFirst(x, x + 1),
        BlockFirst((x,), (x,), ()),
    ]
    expected = [
        "boolean",
        "boolean",
        "integer",
        "float",
        "string",
        "assignment",
        "block",
        "assignment",
        "block",
    ]
    backend, calls = language_backend
    assert translate(objects, backend) == expected
    assert [label for label, _ in calls] == expected
    assert all(
        obj is original for (_, obj), original in zip(calls, objects, strict=True)
    )


def test_literal_subclasses_keep_numerical_and_generated_results():
    class Integer(int):
        pass

    class Floating(float):
        pass

    class Text(str):
        pass

    objects = [True, False, Integer(2), Floating(1.5), Text("a\n'b")]
    numerical = translate(objects, libstd)
    assert all(
        obj is original for obj, original in zip(numerical, objects, strict=True)
    )
    generated = eval(translate(objects, libpythoncode))
    assert generated == [True, False, 2, 1.5, "a\n'b"]
    assert [type(obj) for obj in generated] == [bool, bool, int, float, str]


def test_boolean_dispatch_remains_independent_of_integer_override():
    class Integer(int):
        pass

    parent = translate.dispatch(int)

    def offset_integer(obj, libsl):
        return parent(obj, libsl) + 100

    try:
        translate.register(int, offset_integer)
        result = translate([True, False, Integer(2)], libstd)
        assert result == [True, False, 102]
        assert type(result[0]) is bool and type(result[1]) is bool
    finally:
        translate.register(int, parent)


def test_boolean_override_can_delegate_to_saved_integer_handler(language_backend):
    backend, calls = language_backend
    integer = translate.dispatch(int)
    previous_bool = translate.dispatch(bool)
    try:
        translate.register(bool, integer)
        assert translate([True, False], backend) == ["integer", "integer"]
        assert calls == [("integer", True), ("integer", False)]
    finally:
        translate.register(bool, previous_bool)


def test_optional_string_conversion_and_required_capability_errors(language_backend):
    class Text(str):
        pass

    backend, calls = language_backend
    del backend.lang.to_str
    text = Text("literal")
    assert translate([text], backend)[0] is text
    assert calls == []

    backend.lang.to_str = Unsupported
    with pytest.raises(Unsupported, match="lang.to_str"):
        translate(text, backend)
    del backend.lang.to_float
    with pytest.raises(Unsupported, match="lang.to_float"):
        translate(1.5, backend)


@pytest.mark.parametrize(
    "metadata, expression, unchanged, expected",
    [
        (FunctionInfo, real.sin(0), Real(2) + 3, 10),
        (OperatorInfo, Real(2) + 3, real.sin(0), 15),
    ],
)
def test_function_and_operator_overrides_delegate_independently(
    metadata, expression, unchanged, expected
):
    parent = translate.dispatch(metadata)
    calls = []

    def offset_result(info, libsl):
        calls.append(info)
        implementation = parent(info, libsl)
        return lambda *args, **kwargs: implementation(*args, **kwargs) + 10

    reference = translate(unchanged, libstd)
    try:
        translate.register(metadata, offset_result)
        assert translate([expression, unchanged], libstd) == [expected, reference]
        assert len(calls) == 1
    finally:
        translate.register(metadata, parent)


@pytest.mark.parametrize("base", [Assign, Block])
def test_statement_overrides_delegate_for_subclasses(language_backend, base):
    class CustomStatement(base):
        pass

    x = Real("x")
    obj = (
        CustomStatement(x, x + 1) if base is Assign else CustomStatement((x,), (x,), ())
    )
    backend, backend_calls = language_backend
    calls = []
    parent = translate.dispatch(base)

    def override(node, libsl):
        calls.append(node)
        return "custom " + parent(node, libsl)

    try:
        translate.register(base, override)
        expected = "custom assignment" if base is Assign else "custom block"
        assert translate([obj], backend) == [expected]
        assert len(calls) == 1 and calls[0] is obj
        assert len(backend_calls) == 1 and backend_calls[0][1] is obj
    finally:
        translate.register(base, parent)
