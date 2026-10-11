"""
symbolite.impl.libjax.vector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translate symbolite.abstract.vector
into values and functions defined in JAX.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import operator
from typing import Any

import jax.numpy as _jnp

from ...core import Unsupported

getitem = operator.getitem

add = _jnp.add
sub = _jnp.subtract
mul = _jnp.multiply
matmul = _jnp.matmul
truediv = _jnp.true_divide
floordiv = _jnp.floor_divide
neg = _jnp.negative
pos = _jnp.positive
invert = _jnp.invert
eq = _jnp.equal
ne = _jnp.not_equal


def sum(values: Any) -> Any:
    """Reduce arrays and finite Python sequences, including under JAX tracing."""
    return _jnp.sum(_jnp.asarray(values))


def prod(values: Any) -> Any:
    """Reduce arrays and finite Python sequences, including under JAX tracing."""
    return _jnp.prod(_jnp.asarray(values))


Vector = Unsupported


del operator, Unsupported
