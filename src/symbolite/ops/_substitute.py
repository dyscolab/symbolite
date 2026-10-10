"""
symbolite.ops._substitute
~~~~~~~~~~~~~~~~~~~~~~~~~

Replace symbols, functions, values, etc by others.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import singledispatch
from typing import Any

from ..abstract.vector import getitem
from ..core.call import Call
from ..core.lang import Assign, Block, BlockInfo
from ..core.symbolite_object import get_symbolite_info
from ..core.value import Value
from ._dispatch import TraversalDispatch
from ._traversal import KEEP, Layer, _fold, _rebuild_result, project


@dataclass(frozen=True)
class _BlockLayer(Layer):
    """Substitution-only view: bind the interface, traverse the body iteratively.

    Data retains the original projection for reconstruction. The interface is
    already mapped simultaneously; only body lines become traversed children.
    """

    inputs: tuple[Value[Any], ...] = ()
    outputs: tuple[Value[Any], ...] = ()


@singledispatch
def substitute(obj: Any, replacements: Mapping[Any, Any]) -> Any:
    """Replace symbols, functions, values, etc by others.

    Parameters
    ----------
    obj
        symbolic expression.
    replacements
        replacement dictionary.

    Notes
    -----
    Replaces named values, functions, and hashable atomic literals
    simultaneously. Compound expressions are not mapping targets; use
    ``ops.traversal.rewrite`` for an explicit subtree policy. Built-in containers
    recurse through keys and values; rewritten duplicate keys raise ValueError.
    Traversed exact built-in lists and dictionaries are fresh containers, even
    without replacements. Other nodes retain identity when their children do.
    Replacement objects are returned as supplied. Foreign leaves, including
    arrays and unadapted container subclasses, are not copied.
    Statements use the same iterative traversal, preserve subclass state, and
    validate rebuilt Block dependencies. Block interfaces retain their special
    vector-item substitution policy; the Block name is not substituted.
    """

    def replace(node: Any, layer: Layer) -> Any:
        if layer.kind != "atom":
            return KEEP
        try:
            hash(node)
        except TypeError:
            return KEEP
        return replacements.get(node, KEEP)

    def project_node(node: Any) -> Layer:
        layer = project(node)
        if layer.kind != "object" or not isinstance(node, Block):
            return layer
        info = get_symbolite_info(node)
        if not isinstance(info, BlockInfo):
            return layer
        inputs, _ = _subs(info.inputs, replacements)
        outputs, out_vec = _subs(info.outputs, replacements)
        return _BlockLayer(
            "block_substitution",
            layer,
            info.lines,
            inputs + out_vec if out_vec else inputs,
            outputs,
        )

    def combine(node: Any, layer: Layer, children: tuple[Any, ...]) -> Any:
        if isinstance(layer, _BlockLayer):
            info = get_symbolite_info(node)
            lines = (
                info.lines
                if all(a is b for a, b in zip(info.lines, children, strict=True))
                else children
            )
            return _rebuild_result(
                node, layer.data, (layer.inputs, layer.outputs, lines, info.name)
            )
        return _rebuild_result(node, layer, children)

    return _fold(
        obj,
        combine,
        _dispatch.visit(replacements),
        replace,
        project_node=project_node,
    )


_dispatch = TraversalDispatch(substitute)


# Keep specific dispatch entries so broad wrapper overrides do not displace
# statement behavior. Saved parent handlers can still delegate to the fold.
for _type in (Assign, Block):
    substitute.register(_type, substitute.dispatch(object))


def is_vector_item(el: Value[Any]) -> tuple[bool, tuple[Any, ...]]:
    info = get_symbolite_info(el)
    if not isinstance(info.value, Call):
        return False, ()
    call = info.value
    call_info = get_symbolite_info(call)
    if call_info.func is not getitem:
        return False, ()
    return True, call_info.args


def _subs(
    content: tuple[Value[Any], ...], mapper: Mapping[Any, Any]
) -> tuple[tuple[Value[Any], ...], tuple[Value[Any], ...]]:
    out: list[Value[Any]] = []
    vec_added: list[Value[Any]] = []
    for el in content:
        if el not in mapper:
            out.append(el)
            continue
        mapped = mapper[el]
        sel, args = is_vector_item(mapped)
        if sel:
            var, _ndx = args
            if var not in out:
                out.append(var)
                vec_added.append(var)
        else:
            out.append(mapped)

    result = tuple(out)
    if len(content) == len(result) and all(
        a is b for a, b in zip(content, result, strict=True)
    ):
        result = content
    return result, tuple(vec_added)
