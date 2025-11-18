"""
symbolite.ops
~~~~~~~~~~~~~

Operations to inspect and manipulate symbolic structures:

- as_code: Convert a symbolite object to python code.
- translate: Translate a symbolite object using a backend module.
- substitue: replac

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from ._as_code import as_code
from ._get_name import get_name, get_namespace
from ._substitute import substitute
from ._translate import translate
from ._tree_view import tree_view
from ._yield_named import yield_named
from .base import count_named

__all__ = [
    "count_named",
    "as_code",
    "get_name",
    "get_namespace",
    "substitute",
    "translate",
    "tree_view",
    "yield_named",
]
