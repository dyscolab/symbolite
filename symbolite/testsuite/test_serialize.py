import pickle

from pytest import mark

from .. import Real, Symbol, Vector


@mark.parametrize("cls", [Real, Symbol, Vector])
def test_pickle(cls):
    obj = cls()
    dump = pickle.dumps(obj)
    load = pickle.loads(dump)
    assert load == obj
