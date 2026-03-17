from typing import Callable

import pytest

from ..abstract import real as abstract_real
from ..impl import liblatex
from ..impl.liblatex._latexexpr import LatexExpr

x, y, z = map(abstract_real.Real, "x y z".split())
dummy_reals = (x, y, z)

all_funcs = {impl: getattr(liblatex.real, impl) for impl in liblatex.real.__all__}


@pytest.mark.parametrize("func", all_funcs.values(), ids=all_funcs.keys())
def test_all_real_funcs_run(func: Callable | LatexExpr):
    if func == liblatex.real.Real:
        assert isinstance(func("x"), LatexExpr)
        return
    # TODO: set what each function should be tested as
    try:
        # Test as unary function
        func(*dummy_reals[:1])
    except IndexError:
        # Test as binary function
        func(*dummy_reals[:2])
    except TypeError:
        # Test as named value
        assert isinstance(func, LatexExpr)
