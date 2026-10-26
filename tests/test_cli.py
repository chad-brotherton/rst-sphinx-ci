"""Tests for the usd-inspect command."""

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from usd_inspect.cli import main

ROOT = Path(__file__).resolve().parent.parent
SCENES = ROOT / "examples" / "scenes"
CLI_PAGE = ROOT / "docs" / "source" / "cli.rst"


@pytest.fixture(autouse=True)
def run_from_root(monkeypatch):
    # The docs show paths relative to the repository root.
    monkeypatch.chdir(ROOT)


def test_list_prims(capsys):
    assert main([str(SCENES / "simple.usda")]) == 0
    assert capsys.readouterr().out.split() == [
        "/World", "Xform", "/World/Box", "Cube", "/World/Ball", "Sphere",
    ]


def test_prim_attributes(capsys):
    assert main([str(SCENES / "simple.usda"), "--prim", "/World/Box"]) == 0
    assert capsys.readouterr().out == "size  double  2.0\n"


def test_check_missing_files(capsys):
    assert main([str(SCENES / "broken_layout.usda"), "--check"]) == 1
    out = capsys.readouterr().out
    assert "/World/MissingCrate" in out
    assert "/World/MissingPayload" in out


def test_check_no_missing_files(capsys):
    assert main([str(SCENES / "layout.usda"), "--check"]) == 0
    assert capsys.readouterr().out == "No missing files.\n"


@pytest.mark.parametrize(
    "args, message",
    [
        (["nope.usda"], "no such file"),
        ([str(SCENES / "simple.usda"), "--prim", "/Nope"], "no prim at /Nope"),
        ([str(SCENES / "simple.usda"), "--prim", "World"], "not a valid absolute prim path"),
        ([str(SCENES / "simple.usda"), "--prim", "/World", "--check"], "not allowed with"),
    ],
)
def test_errors_exit_2(capsys, args, message):
    with pytest.raises(SystemExit) as exit_info:
        main(args)
    assert exit_info.value.code == 2
    assert message in capsys.readouterr().err


def test_console_script_hides_usd_warnings():
    script = Path(sys.executable).with_name("usd-inspect" + (".exe" if os.name == "nt" else ""))
    result = subprocess.run(
        [str(script), str(SCENES / "broken_layout.usda"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "MissingCrate" in result.stdout
    assert result.stderr == ""


def _console_examples():
    """Yield (command, expected output) for each ``console`` block in cli.rst."""
    blocks = re.findall(r"\.\. code-block:: console\n\n((?:   .*\n|\n)+)", CLI_PAGE.read_text())
    for block in blocks:
        lines = [line[3:] for line in block.strip("\n").splitlines()]
        command = lines[0].removeprefix("$ ")
        yield pytest.param(command, "\n".join(lines[1:]) + "\n", id=command)


@pytest.mark.parametrize("command, expected", list(_console_examples()))
def test_cli_page_examples(capsys, command, expected):
    """The output shown on the CLI page must match what the command prints."""
    program, *args = shlex.split(command)
    assert program == "usd-inspect"
    main(args)
    assert capsys.readouterr().out == expected
