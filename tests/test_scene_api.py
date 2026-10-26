"""Tests for the usd_inspect scene API, run against the generated scenes."""

from pathlib import Path

import pytest
from pxr import Gf

from usd_inspect import (
    AttributeInfo,
    MissingAsset,
    PrimInfo,
    find_missing_assets,
    list_attributes,
    list_prims,
    open_stage,
)

SCENES = Path(__file__).resolve().parent.parent / "examples" / "scenes"


@pytest.fixture(scope="module")
def simple():
    return open_stage(SCENES / "simple.usda")


def test_open_stage_accepts_str_and_path():
    assert open_stage(SCENES / "simple.usda").GetDefaultPrim().GetName() == "World"
    assert open_stage(str(SCENES / "simple.usda")).GetDefaultPrim().GetName() == "World"


def test_open_stage_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        open_stage(tmp_path / "nope.usda")


def test_open_stage_not_usd(tmp_path):
    bad = tmp_path / "bad.usda"
    bad.write_text("this is not a USD file\n")
    with pytest.raises(ValueError):
        open_stage(bad)


def test_list_prims_simple(simple):
    assert list_prims(simple) == [
        PrimInfo("/World", "Xform"),
        PrimInfo("/World/Box", "Cube"),
        PrimInfo("/World/Ball", "Sphere"),
    ]


def test_list_prims_includes_referenced_children():
    prims = list_prims(open_stage(SCENES / "layout.usda"))
    assert PrimInfo("/World/CrateA/Body", "Cube") in prims
    assert PrimInfo("/World/CrateC/Body", "Cube") in prims


def test_list_attributes_authored_only(simple):
    assert list_attributes(simple, "/World/Box") == [AttributeInfo("size", "double", 2.0)]


def test_list_attributes_values(simple):
    attrs = {attr.name: attr for attr in list_attributes(simple, "/World/Ball")}
    assert sorted(attrs) == ["radius", "userProperties:label", "xformOp:translate", "xformOpOrder"]
    assert attrs["radius"].value == 1.0
    assert attrs["userProperties:label"].value == "bouncy ball"
    assert attrs["xformOp:translate"].type_name == "double3"
    assert attrs["xformOp:translate"].value == Gf.Vec3d(3, 0, 1)


def test_list_attributes_prim_without_attributes(simple):
    assert list_attributes(simple, "/World") == []


@pytest.mark.parametrize("prim_path", ["/World/Nope", "World/Ball", "not a path", ""])
def test_list_attributes_bad_path(simple, prim_path):
    with pytest.raises(ValueError):
        list_attributes(simple, prim_path)


def test_find_missing_assets_broken():
    assert find_missing_assets(open_stage(SCENES / "broken_layout.usda")) == [
        MissingAsset("/World/MissingCrate", "reference", "./props/missing_crate.usda"),
        MissingAsset("/World/MissingPayload", "payload", "./props/missing_payload.usda"),
    ]


@pytest.mark.parametrize("scene", ["simple.usda", "layout.usda", "props/crate.usda"])
def test_find_missing_assets_none(scene):
    assert find_missing_assets(open_stage(SCENES / scene)) == []
