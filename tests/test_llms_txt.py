"""End-to-end tests for scripts/build_llms_txt.py.

The tests build the HTML docs into a temporary folder, run the script on the
result, and check what it writes.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest
from sphinx.cmd.build import build_main

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "build_llms_txt.py"
BASE_URL = "https://chad-brotherton.github.io/rst-sphinx-ci/"
PAGES = ["overview", "installation", "quickstart", "cli", "api", "glossary", "scenes", "pipeline"]


def _run_script(html_dir):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--html", str(html_dir)],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    html_dir = tmp_path_factory.mktemp("html")
    assert build_main(["-q", "-b", "html", str(ROOT / "docs" / "source"), str(html_dir)]) == 0
    result = _run_script(html_dir)
    assert result.returncode == 0, result.stderr
    return html_dir


def test_llms_txt_structure(site):
    text = (site / "llms.txt").read_text()
    assert text.startswith("# USD Scene Inspector\n\n> ")
    assert f"[llms-full.txt]({BASE_URL}llms-full.txt)" in text
    headings = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    assert headings == ["User guide", "Reference", "Optional"]


def test_llms_txt_links_every_page_in_order(site):
    text = (site / "llms.txt").read_text()
    links = re.findall(r"^- \[[^\]]+\]\(([^)]+)\): .+$", text, flags=re.MULTILINE)
    assert links == [f"{BASE_URL}{page}.html.md" for page in PAGES]


def test_pipeline_page_is_optional(site):
    optional = (site / "llms.txt").read_text().split("## Optional", 1)[1]
    assert f"{BASE_URL}pipeline.html.md" in optional


@pytest.mark.parametrize("page", PAGES)
def test_markdown_page_is_clean(site, page):
    markdown = (site / f"{page}.html.md").read_text()
    assert markdown.startswith("# ")
    # No theme navigation, heading anchors, or viewcode links.
    for leftover in ["¶", "headerlink", "[source]", "Skip to main content", "bd-"]:
        assert leftover not in markdown
    # Every link is absolute.
    assert not re.search(r"\]\((?!https?://)", markdown)


def test_code_blocks_keep_their_language(site):
    assert "```console\n$ usd-inspect examples/scenes/simple.usda\n" in (site / "cli.html.md").read_text()
    assert "```pycon\n>>> from usd_inspect import open_stage\n" in (site / "quickstart.html.md").read_text()


def test_admonitions_have_bold_labels(site):
    assert "**Warning:**" in (site / "overview.html.md").read_text()


def test_llms_full_has_every_page_with_its_source(site):
    full = (site / "llms-full.txt").read_text()
    positions = [full.index(f"Source: {BASE_URL}{page}.html\n") for page in PAGES]
    assert positions == sorted(positions)


def test_output_is_deterministic(site):
    names = ["llms.txt", "llms-full.txt"] + [f"{page}.html.md" for page in PAGES]
    before = {name: (site / name).read_bytes() for name in names}
    assert _run_script(site).returncode == 0
    assert {name: (site / name).read_bytes() for name in names} == before


def test_missing_build_fails(tmp_path):
    result = _run_script(tmp_path)
    assert result.returncode != 0
    assert "Build the HTML first" in result.stderr
