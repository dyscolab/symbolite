"""Structural adapters and iterative traversal of Symbolite expressions.

Register project for a custom object type and rebuild for its Layer subclass.
Layer.kind is an open string tag; children alone determine traversal order.
Use fold for bottom-up interpretation, rewrite for pre-descent replacement,
transform for bottom-up replacement, and walk for lazy preorder inspection.
"""

from ._traversal import KEEP, Layer, fold, project, rebuild, rewrite, transform, walk

__all__ = [
    "KEEP",
    "Layer",
    "fold",
    "project",
    "rebuild",
    "rewrite",
    "transform",
    "walk",
]
