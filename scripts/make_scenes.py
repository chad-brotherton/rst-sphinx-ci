"""Generate the test scenes in examples/scenes/.

The docs, doctests, and tests all run against these scenes. Regenerate them
with this script instead of editing the .usda files by hand:

    python scripts/make_scenes.py

The output is deterministic, so running the script twice produces identical
files. A test checks that the committed scenes match a fresh run.
"""

import argparse
from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "examples" / "scenes"

CRATE = "./props/crate.usda"
MISSING_CRATE = "./props/missing_crate.usda"
MISSING_PAYLOAD = "./props/missing_payload.usda"


def _new_stage(path: Path) -> Usd.Stage:
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    return stage


def make_simple(output: Path) -> Path:
    """Write a scene with a few basic prims and attributes."""
    path = output / "simple.usda"
    stage = _new_stage(path)

    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())

    UsdGeom.Cube.Define(stage, "/World/Box").CreateSizeAttr(2.0)

    ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
    ball.CreateRadiusAttr(1.0)
    UsdGeom.XformCommonAPI(ball).SetTranslate(Gf.Vec3d(3, 0, 1))
    label = ball.GetPrim().CreateAttribute("userProperties:label", Sdf.ValueTypeNames.String)
    label.Set("bouncy ball")

    stage.GetRootLayer().Save()
    return path


def make_crate(output: Path) -> Path:
    """Write a small asset that the layout scenes reference."""
    path = output / "props" / "crate.usda"
    stage = _new_stage(path)

    crate = UsdGeom.Xform.Define(stage, "/Crate")
    stage.SetDefaultPrim(crate.GetPrim())
    UsdGeom.Cube.Define(stage, "/Crate/Body").CreateSizeAttr(1.0)

    stage.GetRootLayer().Save()
    return path


def make_layout(output: Path) -> Path:
    """Write a scene whose references and payload all resolve."""
    path = output / "layout.usda"
    stage = _new_stage(path)

    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())

    crate_a = UsdGeom.Xform.Define(stage, "/World/CrateA")
    crate_a.GetPrim().GetReferences().AddReference(CRATE)

    crate_b = UsdGeom.Xform.Define(stage, "/World/CrateB")
    crate_b.GetPrim().GetReferences().AddReference(CRATE)
    UsdGeom.XformCommonAPI(crate_b).SetTranslate(Gf.Vec3d(2, 0, 0))

    crate_c = UsdGeom.Xform.Define(stage, "/World/CrateC")
    crate_c.GetPrim().GetPayloads().AddPayload(CRATE)
    UsdGeom.XformCommonAPI(crate_c).SetTranslate(Gf.Vec3d(4, 0, 0))

    stage.GetRootLayer().Save()
    return path


def make_broken_layout(output: Path) -> Path:
    """Write a scene with one good reference and two broken arcs.

    This scene is authored with the Sdf layer API instead of a stage. A stage
    composes as you edit it, so it would print warnings about the missing files
    while writing a scene that is meant to be broken.
    """
    path = output / "broken_layout.usda"
    path.parent.mkdir(parents=True, exist_ok=True)
    layer = Sdf.Layer.CreateNew(str(path))
    layer.pseudoRoot.SetInfo(UsdGeom.Tokens.upAxis, UsdGeom.Tokens.z)
    layer.defaultPrim = "World"

    world = Sdf.PrimSpec(layer, "World", Sdf.SpecifierDef, "Xform")

    good = Sdf.PrimSpec(world, "CrateA", Sdf.SpecifierDef, "Xform")
    good.referenceList.Prepend(Sdf.Reference(CRATE))

    missing_ref = Sdf.PrimSpec(world, "MissingCrate", Sdf.SpecifierDef, "Xform")
    missing_ref.referenceList.Prepend(Sdf.Reference(MISSING_CRATE))

    missing_payload = Sdf.PrimSpec(world, "MissingPayload", Sdf.SpecifierDef, "Xform")
    missing_payload.payloadList.Prepend(Sdf.Payload(MISSING_PAYLOAD))

    layer.Save()
    return path


SCENES = [make_simple, make_crate, make_layout, make_broken_layout]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"directory to write scenes to (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    for make in SCENES:
        print(f"wrote {make(args.output)}")


if __name__ == "__main__":
    main()
