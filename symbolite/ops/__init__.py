"""
symbolite.core.ops
~~~~~~~~~~~~~~~~~~

Operations to inspect and manipulate symbolic structures:

- as_code: Convert a symbolite object to python code.
- as_function_def: Convert a symbolite object into a python code
  defining a function. Free variables are used as arguments.
- as_function: Convert a symbolite object into an executable
  python code.
- evaluate: Evaluate a symbolite object to return a python type.
- substitue: replac

:copyright: 2023 by Symbolite Authors, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from ._as_code import as_code
from ._as_function import as_function
from ._as_function_def import as_function_def
from ._evaluate_impl import evaluate_impl
from ._get_name import get_name
from ._substitute import substitute
from ._tree_view import tree_view
from ._yield_named import yield_named

__all__ = [
    "as_function",
    "as_function_def",
    "evaluate_impl",
    "get_name",
    "substitute",
    "yield_named",
    "as_code",
    "tree_view",
]
