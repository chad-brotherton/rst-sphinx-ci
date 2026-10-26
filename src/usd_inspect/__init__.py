"""Inspect USD scene files.

USD Scene Inspector reads ``.usda`` and ``.usd`` files with Pixar's ``usd-core``
package. It lists prims and their attributes, and flags references and payloads
whose target files are missing.
"""

from usd_inspect.scene import (
    AttributeInfo,
    MissingAsset,
    PrimInfo,
    find_missing_assets,
    list_attributes,
    list_prims,
    open_stage,
)

__all__ = [
    "open_stage",
    "list_prims",
    "list_attributes",
    "find_missing_assets",
    "PrimInfo",
    "AttributeInfo",
    "MissingAsset",
]

__version__ = "0.1.0"
