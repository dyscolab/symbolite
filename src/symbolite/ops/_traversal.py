"""Shared structure and iterative traversal of symbolic expressions.

Operation handlers can prune traversal with ``visit`` or ``descend``.
Shared subtrees are visited per occurrence; active ancestors alone are tracked
for cycle detection. Foreign objects and unadapted container subclasses are
atomic. Register a projection and, if needed, a Layer subclass rebuilder to
adapt additional structures.
"""

from collections.abc import Callable, Iterator
from copy import copy
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any

from ..core.call import Call, CallInfo
from ..core.function import Function, Operator, UserFunction
from ..core.lang import AssignInfo, BlockInfo, _validate_block_dependencies
from ..core.symbolite_object import (
    SymboliteObject,
    get_symbolite_info,
    set_symbolite_info,
)
from ..core.value import Name, Value, ValueInfo


@dataclass(frozen=True)
class Layer:
    """One level of structure, with original data used for reconstruction.

    ``data`` is heterogeneous adapter metadata, never recursively traversed.
    ``children`` alone defines traversal order. Custom Layer subclasses can
    register their own ``rebuild`` implementation.
    """

    kind: str
    data: Any
    children: tuple[Any, ...] = ()


@singledispatch
def project(obj: Any) -> Layer:
    return Layer("atom", obj)


@project.register(SymboliteObject)
def project_object(obj: SymboliteObject[Any]) -> Layer:
    return Layer("object", obj, tuple(get_symbolite_info(obj)))


@project.register(Function | Operator | UserFunction)
def project_function(obj: SymboliteObject[Any]) -> Layer:
    return Layer("atom", obj)


@project.register(Value)
def project_value(obj: Value[Any]) -> Layer:
    value = get_symbolite_info(obj).value
    if isinstance(value, Name):
        return Layer("atom", obj)
    return Layer("value", obj, (value,))


@project.register(Call)
@project.register(CallInfo)
def project_call(obj: Call | CallInfo) -> Layer:
    info = get_symbolite_info(obj) if isinstance(obj, Call) else obj
    children = (info.func, *info.args, *(v for _, v in info.kwargs_items))
    return Layer("call", obj, children)


@project.register(ValueInfo)
@project.register(AssignInfo)
@project.register(BlockInfo)
def project_record(obj: Any) -> Layer:
    return Layer("record", type(obj), tuple(obj))


@project.register(tuple)
def project_tuple(obj: tuple[Any, ...]) -> Layer:
    if type(obj) is not tuple:
        return Layer("atom", obj)
    return Layer("tuple", None, obj)


@project.register(list)
def project_list(obj: list[Any]) -> Layer:
    if type(obj) is not list:
        return Layer("atom", obj)
    return Layer("list", None, tuple(obj))


@project.register(dict)
def project_dict(obj: dict[Any, Any]) -> Layer:
    if type(obj) is not dict:
        return Layer("atom", obj)
    return Layer("dict", None, tuple(child for pair in obj.items() for child in pair))


def call_parts(
    layer: Layer, children: tuple[Any, ...]
) -> tuple[Any, tuple[Any, ...], dict[str, Any]]:
    obj = layer.data
    info = get_symbolite_info(obj) if isinstance(obj, Call) else obj
    nargs = len(info.args)
    keys = tuple(k for k, _ in info.kwargs_items)
    kwargs = dict(zip(keys, children[1 + nargs :], strict=True))
    return children[0], children[1 : 1 + nargs], kwargs


def pairs(children: tuple[Any, ...]) -> tuple[tuple[Any, Any], ...]:
    return tuple(zip(children[::2], children[1::2], strict=True))


def _validate_block_result(obj: Any) -> None:
    info = get_symbolite_info(obj) if isinstance(obj, SymboliteObject) else obj
    if isinstance(info, BlockInfo):
        _validate_block_dependencies(info)


def _with_info(
    obj: SymboliteObject[Any], info: Any, *, validate_blocks: bool = True
) -> SymboliteObject[Any]:
    if validate_blocks:
        _validate_block_result(info)
    # Copy only the wrapper, preserving subclass state without assuming its
    # constructor has Value/Call's signature. Array children retain identity.
    result = copy(obj)
    if result is obj or type(result) is not type(obj):
        raise TypeError(
            f"Cannot rebuild {type(obj).__name__}: copying must return a new "
            "wrapper of the same type. Register a structural adapter."
        )
    set_symbolite_info(result, info)
    return result


@singledispatch
def rebuild(layer: Layer, children: tuple[Any, ...]) -> Any:
    """Reconstruct a layer, validating Blocks and rejecting dictionary collisions."""
    return _rebuild_builtin(layer, children)


def _rebuild_builtin(
    layer: Layer, children: tuple[Any, ...], *, validate_blocks: bool = True
) -> Any:
    """Default reconstruction; only transform may defer built-in Block checks."""
    match layer.kind:
        case "atom":
            return layer.data
        case "value":
            return _with_info(layer.data, ValueInfo(children[0]))
        case "object":
            info = get_symbolite_info(layer.data)
            return _with_info(
                layer.data, type(info)(*children), validate_blocks=validate_blocks
            )
        case "record":
            info = layer.data(*children)
            if validate_blocks:
                _validate_block_result(info)
            return info
        case "call":
            func, args, kwargs = call_parts(layer, children)
            info = CallInfo(func, args, tuple(kwargs.items()))
            if isinstance(layer.data, Call):
                return _with_info(layer.data, info)
            return info
        case "tuple":
            return children
        case "list":
            return list(children)
        case "dict":
            result: dict[Any, Any] = {}
            for key, value in pairs(children):
                if key in result:
                    raise ValueError("Rewriting produced duplicate dictionary keys.")
                result[key] = value
            return result
        case _:
            raise TypeError(f"No rebuilder for layer kind {layer.kind!r}.")


_DEFAULT_REBUILDER = rebuild.dispatch(object)


KEEP = object()


@dataclass
class _Frame:
    obj: Any
    layer: Layer
    remaining: Iterator[Any]
    results: list[Any] = field(default_factory=list)


def _fold(
    obj: Any,
    combine: Callable[[Any, Layer, tuple[Any, ...]], Any],
    visit: Callable[[Any], Any] | None,
    replace_layer: Callable[[Any, Layer], Any] | None = None,
    *,
    project_node: Callable[[Any], Layer] = project,
) -> Any:
    """Shared stack engine, with optional operation-local projection policy."""
    stack: list[_Frame] = []
    active: set[int] = set()
    node = obj
    while True:
        result = KEEP if visit is None else visit(node)
        if result is KEEP:
            if id(node) in active:
                raise ValueError(
                    f"Cycle detected while traversing {type(node).__name__}."
                )
            layer = project_node(node)
            result = KEEP if replace_layer is None else replace_layer(node, layer)
            if result is KEEP:
                if layer.children:
                    remaining = iter(layer.children)
                    stack.append(_Frame(node, layer, remaining))
                    active.add(id(node))
                    node = next(remaining)
                    continue
                result = combine(node, layer, ())

        while stack:
            frame = stack[-1]
            frame.results.append(result)
            # A child can itself be KEEP: detect exhaustion, not a sentinel.
            try:
                node = next(frame.remaining)
            except StopIteration:
                pass
            else:
                break
            # Run user code outside the StopIteration exception handler so
            # backend failures do not acquire an unrelated exception context.
            stack.pop()
            active.remove(id(frame.obj))
            result = combine(frame.obj, frame.layer, tuple(frame.results))
        else:
            return result


def fold(
    obj: Any,
    algebra: Callable[[Layer, tuple[Any, ...]], Any],
    *,
    visit: Callable[[Any], Any] | None = None,
) -> Any:
    """Combine bottom-up; visit overrides take precedence and prune.

    A visit result of KEEP requests normal traversal. Any other result is
    final for that occurrence and is not traversed again.
    """
    return _fold(obj, lambda _node, layer, children: algebra(layer, children), visit)


def _rebuild_result(
    node: Any,
    layer: Layer,
    children: tuple[Any, ...],
    *,
    defer_block_validation: bool = False,
) -> Any:
    """Copy built-in mutable containers and otherwise reuse unchanged nodes."""
    if type(node) not in (list, dict) and all(
        a is b for a, b in zip(layer.children, children, strict=True)
    ):
        return node
    rebuilder = rebuild.dispatch(type(layer))
    if defer_block_validation and rebuilder is _DEFAULT_REBUILDER:
        return _rebuild_builtin(layer, children, validate_blocks=False)
    return rebuilder(layer, children)


def rewrite(
    obj: Any,
    replace: Callable[[Any], Any],
    *,
    replace_layer: Callable[[Any, Layer], Any] | None = None,
) -> Any:
    """Replace before descent, copying traversed built-in lists and dictionaries.

    Return KEEP to descend; any other result is final for that occurrence.
    Optional ``replace_layer`` runs after projection, only when ``replace``
    returned KEEP, and uses the same replacement convention. Projection is
    performed once per unreplaced occurrence.

    Other nodes retain identity when their children do. Parents containing
    copied containers are rebuilt. Replacement objects and operation overrides
    remain responsible for their own ownership; foreign leaves are not copied.
    """
    return _fold(obj, _rebuild_result, replace, replace_layer)


def transform(obj: Any, rule: Callable[[Any], Any]) -> Any:
    """Apply a rule bottom-up, copying traversed built-in lists and dictionaries.

    The rule sees each node with its children already transformed. Return
    KEEP to retain that node, or a replacement which is not traversed again.
    Shared subtrees are processed once per occurrence, without memoization.
    Other nodes retain identity when their children do. A rule returning KEEP
    retains the rebuilt node, including any fresh containers. Explicit rule
    replacements and foreign leaves are not copied.
    Built-in Block reconstruction defers dependency validation until after its
    rule, so the rule can repair the transformed interface. Block and BlockInfo
    results are then validated, including explicit rule replacements. Direct
    rebuild calls and custom rebuilders retain their own validation behavior.
    """

    def combine(node: Any, layer: Layer, children: tuple[Any, ...]) -> Any:
        updated = _rebuild_result(node, layer, children, defer_block_validation=True)
        result = rule(updated)
        result = updated if result is KEEP else result
        _validate_block_result(result)
        return result

    return _fold(obj, combine, None)


def walk(obj: Any, *, descend: Callable[[Any], bool] | None = None) -> Iterator[Any]:
    """Stream preorder nodes, with optional subtree pruning and cycle checks."""
    stack: list[tuple[int | None, Iterator[Any]]] = [(None, iter((obj,)))]
    active: set[int] = set()
    while stack:
        parent, remaining = stack[-1]
        try:
            node = next(remaining)
        except StopIteration:
            stack.pop()
            if parent is not None:
                active.remove(parent)
            continue

        if id(node) in active:
            raise ValueError(f"Cycle detected while traversing {type(node).__name__}.")
        yield node
        if descend is not None and not descend(node):
            continue
        layer = project(node)
        if layer.children:
            active.add(id(node))
            stack.append((id(node), iter(layer.children)))
