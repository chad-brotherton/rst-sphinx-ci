"""Tests for the generated scenes in examples/scenes/."""

import subprocess
import sys
from pathlib import Path

import pytest
from pxr import Usd

REPO = Path(__file__).resolve().parent.parent
SCENES = REPO / "examples" / "scenes"
SCRIPT = REPO / "scripts" / "make_scenes.py"

SCENE_FILES = [
    "simple.usda",
    "props/crate.usda",
    "layout.usda",
    "broken_layout.usda",
]


@pytest.fixture(scope="module")
def fresh_scenes(tmp_path_factory):
    """Run make_scenes.py into a temporary directory and return that directory."""
    output = tmp_path_factory.mktemp("scenes")
    subprocess.run([sys.executable, str(SCRIPT), "--output", str(output)], check=True)
    return output


@pytest.mark.parametrize("name", SCENE_FILES)
def test_committed_scene_matches_script(fresh_scenes, name):
    committed = SCENES / name
    assert committed.exists(), f"{name} is missing; run scripts/make_scenes.py"
    assert committed.read_bytes() == (fresh_scenes / name).read_bytes(), (
        f"{name} differs from the script's output; run scripts/make_scenes.py "
        "instead of editing scenes by hand"
    )


def test_script_writes_only_known_scenes(fresh_scenes):
    written = sorted(p.relative_to(fresh_scenes).as_posix() for p in fresh_scenes.rglob("*.usda"))
    assert written == sorted(SCENE_FILES)


@pytest.mark.parametrize("name", SCENE_FILES)
def test_scene_opens(name):
    assert Usd.Stage.Open(str(SCENES / name))


def test_simple_scene_prims():
    stage = Usd.Stage.Open(str(SCENES / "simple.usda"))
    prims = {str(p.GetPath()): p.GetTypeName() for p in stage.Traverse()}
    assert prims == {
        "/World": "Xform",
        "/World/Box": "Cube",
        "/World/Ball": "Sphere",
    }


def test_layout_has_no_composition_errors():
    stage = Usd.Stage.Open(str(SCENES / "layout.usda"))
    assert stage.GetCompositionErrors() == []


def test_layout_references_compose():
    stage = Usd.Stage.Open(str(SCENES / "layout.usda"))
    for crate in ("CrateA", "CrateB", "CrateC"):
        assert stage.GetPrimAtPath(f"/World/{crate}/Body").IsValid()


def test_broken_layout_has_two_composition_errors():
    stage = Usd.Stage.Open(str(SCENES / "broken_layout.usda"))
    assert len(stage.GetCompositionErrors()) == 2
