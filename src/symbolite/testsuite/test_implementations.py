"""Backend discovery must not disguise broken implementations as missing extras."""

import types

import pytest

from symbolite import impl


@pytest.mark.parametrize(
    "backend, dependency",
    [("libnumpy", "numpy"), ("libjax", "jax"), ("libsympy", "sympy")],
)
def test_discovery_skips_only_missing_optional_root_dependencies(
    monkeypatch, backend, dependency
):
    original = impl.importlib.import_module

    def import_module(name, package=None):
        if package == "symbolite.impl" and name == f".{backend}":
            raise ModuleNotFoundError(
                f"No module named {dependency!r}", name=dependency
            )
        return original(name, package)

    monkeypatch.setattr(impl.importlib, "import_module", import_module)
    assert backend not in impl.get_all_implementations()


@pytest.mark.parametrize(
    "error",
    [
        ImportError("cannot import name 'AssignInfo' from 'symbolite.abstract.lang'"),
        ModuleNotFoundError("Missing internal module", name="symbolite.core.missing"),
        ModuleNotFoundError("Missing dependency submodule", name="sympy.missing"),
        ModuleNotFoundError("Broken dependency installation", name="mpmath"),
    ],
)
def test_discovery_propagates_internal_import_failures(monkeypatch, error):
    original = impl.importlib.import_module

    def import_module(name, package=None):
        if package == "symbolite.impl" and name == ".libsympy":
            raise error
        return original(name, package)

    monkeypatch.setattr(impl.importlib, "import_module", import_module)
    with pytest.raises(type(error)) as caught:
        impl.get_all_implementations()
    assert caught.value is error


@pytest.mark.parametrize("missing_module", ["sympy", None])
def test_discovery_does_not_treat_unrelated_missing_packages_as_optional(
    monkeypatch, missing_module
):
    original = impl.importlib.import_module
    error = ModuleNotFoundError("Unexpected missing dependency", name=missing_module)

    def import_module(name, package=None):
        if package == "symbolite.impl" and name == ".libstd":
            raise error
        return original(name, package)

    monkeypatch.setattr(impl.importlib, "import_module", import_module)
    with pytest.raises(ModuleNotFoundError) as caught:
        impl.get_all_implementations()
    assert caught.value is error


def test_discovery_kind_filter_is_preserved():
    modules = impl.get_all_implementations((impl.Kind.VALUE, impl.Kind.CODE))
    assert "libstd" in modules and "libpythoncode" in modules and "liblatex" in modules
    assert all(isinstance(module, types.ModuleType) for module in modules.values())
    for kind in impl.Kind:
        assert impl.get_all_implementations(kind) == {
            name: module for name, module in modules.items() if module.KIND is kind
        }
