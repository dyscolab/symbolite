import inspect
import types
from typing import Any

import pytest

from symbolite import Symbol, real
from symbolite.abstract.lang import Assign, Block
from symbolite.core.value import Value
from symbolite.impl import get_all_implementations
from symbolite.ops import substitute, translate
from symbolite.ops.base import free_values, value_names

all_impl = get_all_implementations()

x, y, z = map(real.Real, "x y z".split())

xsy = real.Real("xsy")


def _make_block_from_variable(expr: Value[Any], *, name: str = "f") -> Block:
    result = expr.__class__("__result")
    return Block(
        inputs=free_values(expr),
        outputs=(result,),
        lines=(Assign(result, expr),),
        name=name,
    )


def _block_factory_f1() -> Block:
    result = real.Real("result")
    return Block(
        inputs=(x, y),
        outputs=(result,),
        lines=(Assign(result, 2 * x + y),),
        name="f",
    )


def _block_factory_f2() -> Block:
    total = real.Real("total")
    triple = real.Real("triple")
    quadruple = real.Real("quadruple")
    return Block(
        inputs=(x, y, z),
        outputs=(total, triple, quadruple),
        lines=(
            Assign(total, 2 * x + y),
            Assign(triple, 3 * x),
            Assign(quadruple, 4 * z),
        ),
        name="f",
    )


def _block_factory_f3() -> Block:
    total = real.Real("total")
    triple = real.Real("triple")
    quadruple = real.Real("quadruple")
    result: Value[Any] = Value("result")
    return Block(
        inputs=(x, y, z),
        outputs=(result,),
        lines=(
            Assign(total, 2 * x + y),
            Assign(triple, 3 * x),
            Assign(quadruple, 4 * z),
            Assign(
                result,
                {
                    "a": total,
                    "b": triple,
                    "c": quadruple,
                },
            ),
        ),
        name="f",
    )


@pytest.mark.mypy_testing
def test_typing():
    reveal_type(x + y)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(2 + y)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(x + 2)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(x + xsy)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(xsy + x)  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(real.cos(x))  # R: symbolite.abstract.real.Real # noqa: F821
    reveal_type(real.cos(xsy))  # R: symbolite.abstract.real.Real # noqa: F821


@pytest.mark.parametrize(
    "expr",
    [
        x + y,
        x - y,
        x * y,
        x / y,
        x**y,
        x // y,
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_known_symbols(expr: Value, libsl: types.ModuleType):
    block = _make_block_from_variable(expr)
    f = translate(block, libsl=libsl)
    if inspect.isfunction(f):
        assert f.__name__ == "f"
        assert translate(substitute(expr, {x: 2, y: 3}), libsl=libsl) == f(2, 3)
        assert tuple(inspect.signature(f).parameters.keys()) == ("x", "y")


@pytest.mark.parametrize(
    "block_factory,params,args,result",
    [
        (_block_factory_f1, ("x", "y"), (2, 3), 7),
        (_block_factory_f2, ("x", "y", "z"), (2, 3, 1), (7, 6, 4)),
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_block_execution(block_factory, params, args, result, libsl: types.ModuleType):
    block = block_factory()
    f = translate(block, libsl=libsl)
    if inspect.isfunction(f):
        assert f.__name__ == "f"
        assert tuple(inspect.signature(f).parameters.keys()) == params
        assert f(*args) == result


@pytest.mark.parametrize(
    "expr,replaced",
    [
        (x + real.cos(y), 2 + real.cos(3)),
        (x + real.pi * y, 2 + real.pi * 3),
    ],
)
@pytest.mark.parametrize("libsl", all_impl.values(), ids=all_impl.keys())
def test_lib_symbols(expr: Value[Any], replaced: Symbol, libsl: types.ModuleType):
    block = _make_block_from_variable(expr)
    f = translate(block, libsl=libsl)
    if inspect.isfunction(f):
        value = f(2, 3)
        assert f.__name__ == "f"
        assert translate(substitute(expr, {x: 2, y: 3}), libsl=libsl) == value
        assert tuple(inspect.signature(f).parameters.keys()) == ("x", "y")


@pytest.mark.parametrize(
    "expr,namespace,result",
    [
        (
            x + real.pi * real.cos(y),
            None,
            {
                "x",
                "y",
                "real.cos",
                "real.pi",
                "real.mul",
                "real.add",
            },
        ),
        (x + real.pi * real.cos(y), "", {"x", "y"}),
        (
            x + real.pi * real.cos(y),
            "real",
            {"real.cos", "real.pi", "real.mul", "real.add"},
        ),
    ],
)
def test_list_symbols(expr: Value[Any], namespace: str | None, result: Symbol):
    assert value_names(expr, namespace) == result
