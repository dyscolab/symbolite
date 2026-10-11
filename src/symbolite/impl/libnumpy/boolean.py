"""Elementwise logical composition of Boolean scalars and NumPy masks."""

import numpy as np

from ...core import Unsupported

and_ = np.logical_and
or_ = np.logical_or
xor = np.logical_xor

Boolean = Unsupported
