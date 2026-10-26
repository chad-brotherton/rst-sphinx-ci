# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from importlib.metadata import version as _package_version
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "USD Scene Inspector"
copyright = "2026, Chad Brotherton"
author = "Chad Brotherton"

# Read the version from the installed package so the docs and the code never
# disagree. Requires `pip install -e .` before building.
release = _package_version("usd-scene-inspector")
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

exclude_patterns = []

# -- Options for autodoc and napoleon ----------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"

napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- Options for doctest -----------------------------------------------------
# Code samples run against the scenes that scripts/make_scenes.py generates.
# Use SCENES in samples instead of hard-coding paths.

_SCENES = Path(__file__).resolve().parents[2] / "examples" / "scenes"

doctest_global_setup = f"""
from pathlib import Path
SCENES = Path({str(_SCENES)!r})
"""

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_title = f"{project} {version}"
html_theme_options = {
    "github_url": "https://github.com/chad-brotherton/rst-sphinx-ci",
    "navigation_with_keys": False,
}

# Strip prompts and output when readers copy code samples.
copybutton_exclude = ".linenos, .gp, .go"
