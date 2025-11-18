import math

import pytest

from symbolite import real
from symbolite.abstract.lang import Assign, Block
from symbolite.core.symbolite_object import get_symbolite_info
from symbolite.impl import libpythoncode, libstd
from symbolite.ops import translate


def _make_sample_block() -> tuple[Block, str]:
    x = real.Real("x")
    y = real.Real("y")
    total = real.Real("total")
    cosine = real.Real("cosine")

    block = Block(
        inputs=(x, y),
        outputs=(total, cosine),
        lines=(
            Assign(total, x + y),
            Assign(cosine, real.cos(total)),
        ),
    )

    expected_definition = (
        "def __symbolite_block(x: real.Real, y: real.Real) -> tuple[real.Real, real.Real]:\n"
        "    total = x + y\n"
        "    cosine = real.cos(total)\n"
        "    return total, cosine"
    )

    return block, expected_definition


def test_block_translate_to_code_definition():
    block, expected_definition = _make_sample_block()

    code = translate(block, libpythoncode)

    assert isinstance(code, str)
    assert code == expected_definition


def test_block_translate_to_callable():
    block, expected_definition = _make_sample_block()

    func = translate(block, libstd)

    assert callable(func)
    assert func.__name__ == "__symbolite_block"
    assert func.__symbolite_def__ == expected_definition
    assert func.__symbolite_block__ == get_symbolite_info(block)

    value = func(2, 3)
    assert isinstance(value, tuple)
    assert value[0] == 5
    assert value[1] == pytest.approx(math.cos(5))


def test_block_requires_defined_user_variables():
    x = real.Real("x")
    total = real.Real("total")
    orphan = real.Real("orphan")

    block = Block(
        inputs=(x,),
        outputs=(total,),
        lines=(Assign(total, x + orphan),),
    )

    with pytest.raises(ValueError, match="value 'orphan'"):
        translate(block, libpythoncode)


def test_block_requires_defined_outputs():
    x = real.Real("x")
    total = real.Real("total")

    block = Block(
        inputs=(x,),
        outputs=(total,),
        lines=(),
    )

    with pytest.raises(ValueError, match="output value 'total'"):
        translate(block, libpythoncode)


def test_block_custom_name():
    x = real.Real("x")
    y = real.Real("y")
    total = real.Real("total")

    block = Block(
        inputs=(x, y),
        outputs=(total,),
        lines=(Assign(total, x + y),),
        name="add",
    )

    expected_definition = (
        "def add(x: real.Real, y: real.Real) -> real.Real:\n"
        "    total = x + y\n"
        "    return total"
    )

    code = translate(block, libpythoncode)
    assert code == expected_definition

    func = translate(block, libstd)
    assert func.__name__ == "add"
    assert func.__symbolite_def__ == expected_definition
    assert func.__symbolite_block__ == get_symbolite_info(block)


def test_block_assign_translation_uses_backend():
    block, _ = _make_sample_block()

    module = libpythoncode

    original_assign = module.lang.Assign

    def custom_assign(assign, rhs_code=None, **kwargs):
        assert kwargs.get("libsl") is module
        rendered = original_assign(assign, rhs_code=rhs_code, **kwargs)
        return f"{rendered}  # custom"

    module.lang.Assign = custom_assign  # type: ignore[attr-defined]
    try:
        code = translate(block, module)
        assert "# custom" in code
    finally:
        module.lang.Assign = original_assign  # type: ignore[attr-defined]


@pytest.mark.xfail
def test_assign_execution_sets_locals():
    x = real.Real("x")
    y = real.Real("y")
    total = real.Real("total")
    assignment = Assign(total, x + y)

    assert translate(assignment, libstd) == {"total": x + y}


def test_assign_translation_to_code():
    x = real.Real("x")
    y = real.Real("y")
    assignment = Assign(x, y + 1)

    rendered = translate(assignment, libpythoncode)
    assert isinstance(rendered, str)
    assert rendered.startswith("x = ")
