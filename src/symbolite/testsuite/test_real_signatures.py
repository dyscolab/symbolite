import math

import pytest

from symbolite import Real, real, translate
from symbolite.core import Unsupported
from symbolite.core.function import FunctionInfo, VariadicFunction
from symbolite.core.lang import Assign, Block
from symbolite.core.symbolite_object import get_symbolite_info
from symbolite.impl import libjax, liblatex, libnumpy, libstd, libsympy
from symbolite.ops import as_code


@pytest.mark.parametrize(
    "name,arguments,expected",
    [
        ("comb", (5, 2), 10),
        ("copysign", (2, -1), -2.0),
        ("fmod", (-3, 2), -1.0),
        ("nextafter", (1.0, 2.0), math.nextafter(1.0, 2.0)),
    ],
)
def test_binary_public_math_functions_match_standard_library(name, arguments, expected):
    expression = getattr(real, name)(*arguments)
    assert translate(expression, libstd) == expected


@pytest.mark.parametrize("values", [(-3, 2), (3, -2), (-3, -2), (3, 2)])
@pytest.mark.parametrize("libsl", [libstd, libnumpy, libjax, libsympy])
def test_fmod_matches_math_dividend_sign_across_backends(values, libsl):
    assert float(translate(real.fmod(*values), libsl)) == pytest.approx(
        math.fmod(*values)
    )


@pytest.mark.parametrize("name", ["comb", "copysign", "fmod", "nextafter"])
def test_binary_public_math_functions_reject_wrong_positional_count(name):
    function = getattr(real, name)
    with pytest.raises(TypeError):
        function(1)
    with pytest.raises(TypeError):
        function(1, 2, 3)


@pytest.mark.parametrize("values", [(), (3,), (3, 4), (3, 4, 12)])
@pytest.mark.parametrize("libsl", [libstd, libnumpy, libjax, libsympy])
def test_variadic_hypot_matches_math_across_backends(values, libsl):
    result = translate(real.hypot(*values), libsl)
    assert float(result) == pytest.approx(math.hypot(*values))


@pytest.mark.parametrize("libsl", [libstd, libnumpy, libjax])
def test_hypot_contract_and_generated_execution(libsl):
    info = get_symbolite_info(real.hypot)
    assert isinstance(info, FunctionInfo)
    assert isinstance(real.hypot, VariadicFunction)
    assert (info.name, info.arity) == ("hypot", None)

    x, y, z, result = map(Real, ("x", "y", "z", "result"))
    expression = real.hypot(x, y, z)
    assert as_code(expression) == "real.hypot(x, y, z)"
    block = Block((x, y, z), (result,), (Assign(result, expression),))
    assert float(translate(block, libsl)(3, 4, 12)) == pytest.approx(13)


def test_hypot_and_gamma_have_distinct_latex_names():
    x, y, z = map(Real, ("x", "y", "z"))
    assert str(translate(real.hypot(x, y, z), liblatex)) == (
        r"\operatorname{hypot}\left( x, y, z \right)"
    )
    assert str(translate(real.gamma(x), liblatex)) == r"\Gamma\left( x \right)"


def test_sympy_fmod_preserves_symbolic_dependencies():
    x, y = Real("x"), Real("y")
    expression = translate(real.fmod(x, y), libsympy)
    sx, sy = translate(x, libsympy), translate(y, libsympy)
    assert expression.subs({sx: -3, sy: 2}) == -1


@pytest.mark.parametrize(
    "expression,libsl,name",
    [
        (real.comb(5, 2), libnumpy, "comb"),
        (real.comb(5, 2), libjax, "comb"),
        (real.comb(5, 2), libsympy, "comb"),
        (real.copysign(2, -1), libsympy, "copysign"),
        (real.nextafter(1.0, 2.0), libsympy, "nextafter"),
    ],
)
def test_unsupported_public_math_functions_are_explicit(expression, libsl, name):
    with pytest.raises(Unsupported, match=rf"real\.{name}"):
        translate(expression, libsl)


def test_optional_math_forms_remain_outside_the_public_contract():
    with pytest.raises(TypeError):
        real.log(8, 2)
    with pytest.raises(TypeError):
        real.nextafter(1.0, 2.0, steps=3)
