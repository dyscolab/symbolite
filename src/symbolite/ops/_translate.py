"""
symbolite.ops._translate
~~~~~~~~~~~~~~~~~~~~~~~~

Translate a symbolic structure using an implementation.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import types
from collections.abc import Callable
from functools import partial, singledispatch
from operator import attrgetter
from reprlib import Repr
from typing import Any, cast

from ..core import (
    Unsupported,
)
from ..core.call import CallInfo
from ..core.function import (
    Function,
    FunctionInfo,
    Operator,
    OperatorInfo,
    UserFunction,
    UserFunctionInfo,
)
from ..core.lang import Assign, Block, BlockInfo, _validate_block_dependencies
from ..core.symbolite_object import SymboliteObject, get_symbolite_info
from ..core.value import Name, Value
from ..impl import Kind
from ._dispatch import TraversalDispatch
from ._get_name import get_full_name, get_name, get_namespace
from ._traversal import Layer, call_parts, fold, pairs, rebuild, walk


@singledispatch
def translate(obj: Any, libsl: types.ModuleType) -> Any:
    """Translate expression into backend representation.

    Parameters
    ----------
    obj
        symbolic expression.
    libsl
        implementation module.

    Notes
    -----
    Native statement handlers validate structural cycles and Block dependencies
    before backend calls, including payloads mutated after construction. This
    validation does not evaluate expressions; registered overrides still prune
    their subtrees and control their own validation when not delegating.
    Numerical Blocks also resolve vector/Boolean capabilities before compilation,
    so unsupported primitives cannot be bypassed by generated Python operators.
    """

    return fold(
        obj,
        lambda layer, children: translate_layer(layer, children, libsl),
        visit=_dispatch.visit(libsl),
    )


_DESCRIPTIONS = Repr()
_DESCRIPTIONS.maxlevel = 3
_DESCRIPTIONS.maxstring = 100
_DESCRIPTIONS.maxother = 100


def _describe(obj: Any) -> str:
    """Bound diagnostics and preserve backend errors if repr itself fails."""
    try:
        return _DESCRIPTIONS.repr(obj)
    except Exception:  # noqa: BLE001 - diagnostic failures must not mask backend errors
        return f"<{type(obj).__name__}>"


@singledispatch
def translate_layer(
    layer: Layer, children: tuple[Any, ...], libsl: types.ModuleType
) -> Any:
    """Interpret a layer whose children have already been translated.

    Register a handler for a custom Layer subclass to supply backend semantics
    without recursively invoking translate. Object-level translate handlers
    take precedence and prune traversal. Unknown kinds default to rebuild.
    """
    match layer.kind:
        case "atom":
            atom = layer.data
            if isinstance(atom, Value):
                return _resolve_value(atom, libsl)
            if isinstance(atom, (Function, Operator, UserFunction)):
                return translate(
                    get_symbolite_info(cast(SymboliteObject[Any], atom)), libsl
                )
            return atom
        case "value":
            return children[0]
        case "call":
            func, args, kwargs = call_parts(layer, children)
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                ex.add_note(
                    f"While translating {_describe(func)}"
                    f"(*{_describe(args)}, **{_describe(kwargs)})"
                )
                raise
        case "tuple" | "object" | "record":
            return _resolve(libsl, "lang.to_tuple")(children, libsl)
        case "list":
            return _resolve(libsl, "lang.to_list")(children, libsl)
        case "dict":
            return _resolve(libsl, "lang.to_dict")(pairs(children), libsl)
        case _:
            return rebuild(layer, children)


def _resolve(libsl: types.ModuleType, name: str) -> Any:
    try:
        value = attrgetter(name)(libsl)
    except AttributeError as ex:
        raise Unsupported(f"{name} is not supported in module {libsl.__name__}") from ex
    if value is Unsupported:
        raise Unsupported(f"{name} is not supported in module {libsl.__name__}")
    return value


_LANG_TRANSLATORS: dict[type[Any], str] = {
    bool: "to_bool",
    int: "to_int",
    float: "to_float",
    str: "to_str",
    Assign: "Assign",
    Block: "Block",
}


def translate_lang(obj: Any, libsl: types.ModuleType, *, name: str) -> Any:
    """Delegate to the language capability bound by type registration."""
    if name == "to_str" and not hasattr(libsl.lang, name):
        return obj
    translator = _resolve(libsl, f"lang.{name}")
    if name in ("Assign", "Block"):
        capabilities = (
            libsl if name == "Block" and hasattr(libsl.lang, "CODE_IMPL") else None
        )
        _validate_statement(obj, capabilities=capabilities)
    return translator(obj, libsl)


for _type, _name in _LANG_TRANSLATORS.items():
    translate.register(_type, partial(translate_lang, name=_name))


_STATEMENT_HANDLERS = (translate.dispatch(Assign), translate.dispatch(Block))


def _validate_statement(
    obj: Any, *, capabilities: types.ModuleType | None = None
) -> None:
    """Check cycles, optional compiled capabilities, and Block dependencies.

    The root is already routed to a native statement handler, including saved
    parent delegation. Other operation overrides still prune their subtrees.
    No validation state is cached: mutable statement payloads are checked on
    every native translation, including recursive backend calls.
    """
    handler: Callable[..., Any] | None = None
    blocks: list[BlockInfo] = []
    compiled_names: list[str] = []

    def descend(_node: Any) -> bool:
        return handler is None or any(
            handler is parent for parent in _STATEMENT_HANDLERS
        )

    for index, node in enumerate(walk(obj, descend=descend)):
        selected = _dispatch.select(node) if index else None
        handler = None if selected is None else selected[0]
        if capabilities is not None and handler is translate_named_function:
            assert selected is not None
            function_info = selected[1]
            if function_info.namespace in ("vector", "boolean"):
                compiled_names.append(f"{function_info.namespace}.{function_info.name}")
        if not descend(node):
            continue
        info = get_symbolite_info(node) if isinstance(node, SymboliteObject) else node
        if isinstance(info, BlockInfo):
            blocks.append(info)

    for info in blocks:
        _validate_block_dependencies(info)
    if capabilities is not None:
        for name in compiled_names:
            _resolve(capabilities, name)


def _resolve_value(obj: Value[Any], libsl: types.ModuleType) -> Any:
    info = get_symbolite_info(obj)
    assert isinstance(info.value, Name)

    namespace = get_namespace(info)
    if namespace is None or namespace == "":
        # User defined symbol
        # Try to map the class
        cls_name = f"{obj.__class__.__module__.split('.')[-1]}.{obj.__class__.__name__}"

        cls = _resolve(libsl, cls_name)
        return cls(get_name(obj))
    else:
        # Library symbol
        qname = get_full_name(obj)
        return _resolve(libsl, qname)


@translate.register(FunctionInfo)
@translate.register(OperatorInfo)
def translate_named_function(
    obj: FunctionInfo[Any] | OperatorInfo[Any], libsl: types.ModuleType
) -> Any:
    return _resolve(libsl, f"{obj.namespace}.{obj.name}")


@translate.register(UserFunctionInfo)
def translate_user_function_info(
    obj: UserFunctionInfo[Any, Any, Any], libsl: types.ModuleType
) -> Any:
    impls = obj.impls
    default = None
    for k, v in impls:
        if k is libsl:
            return v
        elif k == "default":
            default = v
    if default is not None and getattr(libsl, "KIND", None) != Kind.CODE:
        return default

    if getattr(libsl, "KIND", None) == Kind.CODE:
        raise Unsupported(
            f"Function {obj.name!r} requires an explicit implementation for "
            f"code backend {libsl.__name__}; numerical defaults cannot emit code."
        )

    raise RuntimeError(
        f"No implementation found for {libsl.__name__} and no default implementation provided for function {obj!s}"
    )


# Share the fold handler while retaining explicit dispatch entries: registering
# a SymboliteObject override must not replace Value's more specific behavior.
for _type in (tuple, list, dict, SymboliteObject, Value, CallInfo):
    translate.register(_type, translate.dispatch(object))

_dispatch = TraversalDispatch(
    translate,
    metadata_exclusions=(Value,),
    terminal_handlers=(
        *(translate.dispatch(cls) for cls in (bool, int, float, str)),
        translate_named_function,
        translate_user_function_info,
    ),
)
