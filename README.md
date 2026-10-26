# rst-sphinx-ci

A docs-as-code reference project. It pairs a small Python tool, **USD Scene Inspector**, with a complete
documentation pipeline: reStructuredText and Sphinx, a generated API reference, tested examples, style and spelling
checks in CI, and publishing to GitHub Pages.

**Read the docs:** https://chad-brotherton.github.io/rst-sphinx-ci/

## USD Scene Inspector

`usd-inspect` reads a USD scene with Pixar's `usd-core` package. It lists prims, shows a prim's authored
attributes, and finds references and payloads whose files are missing.

```console
$ usd-inspect examples/scenes/broken_layout.usda --check
/World/MissingCrate    reference  ./props/missing_crate.usda
/World/MissingPayload  payload    ./props/missing_payload.usda
```

## The docs pipeline

Every pull request runs these checks, and `main` requires them to pass:

- `pytest` on Python 3.11 and 3.14, including a test that runs each command-line example in the docs
- `sphinx-build -W`, so a warning such as a broken cross-reference fails the build
- the doctests, which run every Python example in the docs against generated test scenes
- Vale, which fails the build on a spelling error in the docs, this README, or a docstring

Each merge into `main` publishes the site, along with
[`llms.txt`](https://llmstxt.org/), a Markdown copy of each page, and `llms-full.txt` for AI tools. The
[pipeline page](https://chad-brotherton.github.io/rst-sphinx-ci/pipeline.html) explains each step.

## Build it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[docs,test]"
sphinx-build -W -b html docs/source docs/build/html
sphinx-build -b doctest docs/source docs/build/doctest
pytest
```

## License

MIT. See [LICENSE](LICENSE).
