"""
symbolite.ops._substitute
~~~~~~~~~~~~~~~~~~~~~~~~~

Replace symbols, functions, values, etc by others.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from collections.abc import Mapping
from functools import singledispatch
from typing import Any

from ..abstract.vector import getitem
from ..core.call import Call
from ..core.lang import Assign, Block
from ..core.symbolite_object import get_symbolite_info
from ..core.value import Name, Value


@singledispatch
def substitute(obj: Any, replacements: Mapping[Any, Any]) -> Any:
    """Replace symbols, functions, values, etc by others.

    Parameters
    ----------
    obj
        symbolic expression.
    replacements
        replacement dictionary.
    """
    return replacements.get(obj, obj)


@substitute.register(Value)
def substitute_value[R: Value[Any]](obj: R, mapper: Mapping[Any, Any]) -> R:
    info = get_symbolite_info(obj)
    if isinstance(info.value, Name):
        return mapper.get(obj, obj)
    return obj.__class__(substitute(info.value, mapper))


@substitute.register
def substitue_call(obj: Call, mapper: Mapping[Any, Any]) -> Call:
    info = get_symbolite_info(obj)
    func = mapper.get(info.func, info.func)
    args = tuple(substitute(arg, mapper) for arg in info.args)
    kwargs = {k: substitute(arg, mapper) for k, arg in info.kwargs_items}

    return Call(func, args, tuple(kwargs.items()))


@substitute.register
def substitue_assign(obj: Assign, mapper: Mapping[Any, Any]) -> Assign:
    info = get_symbolite_info(obj)
    return Assign(
        substitute(info.lhs, mapper),
        substitute(info.rhs, mapper),
    )


def is_vector_item(el: Value[Any]) -> tuple[bool, tuple[Any, ...]]:
    info = get_symbolite_info(el)
    if not isinstance(info.value, Call):
        return False, ()
    call = info.value
    info = get_symbolite_info(call)
    if info.func is not getitem:
        return False, ()
    return True, info.args


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

    return tuple(out), tuple(vec_added)


@substitute.register
def substitue_block(obj: Block, mapper: Mapping[Any, Any]) -> Block:
    info = get_symbolite_info(obj)

    inputs, _ = _subs(info.inputs, mapper)
    outputs, out_vec = _subs(info.outputs, mapper)

    return Block(
        inputs + out_vec,
        outputs,
        lines=tuple(substitute(el, mapper) for el in info.lines),
        name=info.name,
    )
