import pickle
from typing import Any

from pytest import mark

from .. import Real, Symbol, Vector


@mark.parametrize("cls", [Real, Symbol, Vector])
def test_pickle(cls: Any):
    obj = cls("x")
    dump = pickle.dumps(obj)
    load = pickle.loads(dump)
    assert load == obj
