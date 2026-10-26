"""Read prims, attributes, and missing assets from a USD stage."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pxr import Ar, Sdf, Tf, Usd


@dataclass(frozen=True)
class PrimInfo:
    """A prim on a stage.

    Attributes:
        path: The prim's path, such as ``/World/Ball``.
        type_name: The prim's schema type, such as ``Sphere``. Empty for a prim
            with no type.
    """

    path: str
    type_name: str


@dataclass(frozen=True)
class AttributeInfo:
    """An attribute authored on a prim.

    Attributes:
        name: The attribute's name, such as ``radius``.
        type_name: The attribute's value type, such as ``double``.
        value: The attribute's value at the default time, as a Python or ``pxr``
            object. ``None`` if the attribute has no value.
    """

    name: str
    type_name: str
    value: Any


@dataclass(frozen=True)
class MissingAsset:
    """A reference or payload whose target file can't be found.

    Attributes:
        prim_path: The path of the prim that has the reference or payload.
        arc: ``"reference"`` or ``"payload"``.
        asset_path: The path as it's written in the scene.
    """

    prim_path: str
    arc: str
    asset_path: str


def open_stage(path: str | os.PathLike[str]) -> Usd.Stage:
    """Open a USD file and return its stage.

    Args:
        path: The ``.usda`` or ``.usd`` file to open.

    Returns:
        The opened stage, with all payloads loaded.

    Raises:
        FileNotFoundError: If ``path`` doesn't exist.
        ValueError: If USD can't read the file.

    Example:
        >>> from usd_inspect import list_prims, open_stage
        >>> stage = open_stage(SCENES / "simple.usda")
        >>> list_prims(stage)[0]
        PrimInfo(path='/World', type_name='Xform')
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"no such file: {path}")
    try:
        return Usd.Stage.Open(str(path))
    except Tf.ErrorException as error:
        raise ValueError(f"USD can't read {path}") from error


def list_prims(stage: Usd.Stage) -> list[PrimInfo]:
    """List the prims on a stage, in depth-first order.

    Args:
        stage: The stage to read.

    Returns:
        One entry for each active, defined prim.

    Example:
        >>> from usd_inspect import list_prims, open_stage
        >>> stage = open_stage(SCENES / "simple.usda")
        >>> for prim in list_prims(stage):
        ...     print(prim.path, prim.type_name)
        /World Xform
        /World/Box Cube
        /World/Ball Sphere
    """
    return [PrimInfo(str(prim.GetPath()), str(prim.GetTypeName())) for prim in stage.Traverse()]


def list_attributes(stage: Usd.Stage, prim_path: str) -> list[AttributeInfo]:
    """List the attributes authored on a prim, sorted by name.

    Attributes that only have a schema's default value aren't included.

    Args:
        stage: The stage to read.
        prim_path: The absolute path of the prim, such as ``/World/Ball``.

    Returns:
        One entry for each authored attribute.

    Raises:
        ValueError: If ``prim_path`` isn't a valid absolute path, or no prim
            exists at that path.

    Example:
        >>> from usd_inspect import list_attributes, open_stage
        >>> stage = open_stage(SCENES / "simple.usda")
        >>> for attribute in list_attributes(stage, "/World/Ball"):
        ...     print(attribute.name, attribute.type_name, attribute.value)
        radius double 1.0
        userProperties:label string bouncy ball
        xformOp:translate double3 (3, 0, 1)
        xformOpOrder token[] [xformOp:translate]
    """
    valid, _ = Sdf.Path.IsValidPathString(prim_path)
    if not valid or not Sdf.Path(prim_path).IsAbsolutePath():
        raise ValueError(f"not a valid absolute prim path: {prim_path!r}")
    prim = stage.GetPrimAtPath(prim_path)
    if not prim:
        raise ValueError(f"no prim at {prim_path}")
    return [
        AttributeInfo(attr.GetName(), str(attr.GetTypeName()), attr.Get())
        for attr in prim.GetAuthoredAttributes()
    ]


def find_missing_assets(stage: Usd.Stage) -> list[MissingAsset]:
    """Find references and payloads whose target files can't be found.

    Each asset path is resolved relative to the layer that authors it, the same
    way USD resolves it when it composes the stage. References and payloads to
    other prims in the same file have no asset path and are skipped.

    Args:
        stage: The stage to check.

    Returns:
        One entry for each missing file, in prim order. Empty if every target
        file exists.

    Example:
        >>> from usd_inspect import find_missing_assets, open_stage
        >>> stage = open_stage(SCENES / "broken_layout.usda")
        >>> for missing in find_missing_assets(stage):
        ...     print(missing.prim_path, missing.arc, missing.asset_path)
        /World/MissingCrate reference ./props/missing_crate.usda
        /World/MissingPayload payload ./props/missing_payload.usda
    """
    resolver = Ar.GetResolver()
    missing: dict[MissingAsset, None] = {}
    for prim in stage.Traverse():
        for spec in prim.GetPrimStack():
            arcs = (("reference", spec.referenceList), ("payload", spec.payloadList))
            for arc, list_op in arcs:
                for item in list_op.GetAddedOrExplicitItems():
                    if not item.assetPath:
                        continue
                    anchored = Sdf.ComputeAssetPathRelativeToLayer(spec.layer, item.assetPath)
                    if not resolver.Resolve(anchored):
                        missing[MissingAsset(str(prim.GetPath()), arc, item.assetPath)] = None
    return list(missing)
