"""
symbolite.ops
~~~~~~~~~~~~~

Operations to inspect and manipulate symbolic structures:

- as_code: Convert a symbolite object to python code.
- translate: Translate a symbolite object using a backend module.
- substitute: Replace atomic symbols and values simultaneously.
- translate_layer: Interpret already translated children of a structural layer.
- traversal: Structural adapters, folds, rewrites, and inspection.

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from . import traversal
from ._as_code import as_code
from ._get_name import get_name, get_namespace
from ._substitute import substitute
from ._translate import translate, translate_layer
from ._tree_view import tree_view
from ._yield_named import yield_named
from .base import count_named

__all__ = [
    "as_code",
    "count_named",
    "get_name",
    "get_namespace",
    "substitute",
    "translate",
    "translate_layer",
    "traversal",
    "tree_view",
    "yield_named",
]
