"""Elementwise logical composition of Boolean scalars and JAX masks."""

import jax.numpy as jnp

from ...core import Unsupported

and_ = jnp.logical_and
or_ = jnp.logical_or
xor = jnp.logical_xor

Boolean = Unsupported
