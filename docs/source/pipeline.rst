How these docs are built
========================

These docs are written in reStructuredText, built with Sphinx, tested in CI,
and published to GitHub Pages on every release. This page explains each step,
so you can see how the docs stay accurate as the code changes.

Where the docs live
-------------------

The docs live in the same repository as the code:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Path
     - Contents
   * - ``docs/source/``
     - The reStructuredText pages and ``conf.py``, the Sphinx configuration.
   * - ``src/usd_inspect/``
     - The package. Its docstrings become the :doc:`api`.
   * - ``examples/scenes/``
     - The :ref:`test scenes <test-scenes>` that every example runs against.
   * - ``scripts/build_llms_txt.py``
     - Generates the :ref:`output for AI tools <llms-txt>` from the built site.
   * - ``.vale.ini`` and ``styles/``
     - The style and spelling rules.
   * - ``.github/workflows/docs.yml``
     - The CI workflow that tests, checks, and publishes the docs.

Sphinx extensions
-----------------

``conf.py`` turns on these extensions:

- ``sphinx.ext.autodoc`` and ``sphinx.ext.napoleon`` build the :doc:`api` from
  Google-style docstrings.
- ``sphinx.ext.doctest`` runs the Python examples. See
  :ref:`tested-examples`.
- ``sphinx.ext.intersphinx`` links names like :py:exc:`FileNotFoundError` to
  the Python docs.
- ``sphinx.ext.viewcode`` adds a link from each API entry to its source.
- ``sphinx_copybutton`` adds a copy button to code blocks. It copies only the
  commands, without prompts such as ``$`` and ``>>>`` or their output.
- ``sphinx_design`` provides the tabs on the :doc:`installation` page.

The theme is ``pydata-sphinx-theme``, with a template override that shows the
full table of contents in the left sidebar on every page.

.. _tested-examples:

How the examples are tested
---------------------------

Every example you might copy runs in CI, so an example can't silently go out
of date:

- **Python examples** on the :doc:`quickstart` page and in docstrings are
  doctests. ``sphinx-build -b doctest`` runs them and compares the output.
  They use ``SCENES``, a path defined in ``conf.py``, instead of hard-coded
  paths.
- **Command-line examples** on the :doc:`cli` page can't be doctests, so a
  pytest test reads each ``console`` block, runs the command, and fails if the
  output on the page doesn't match.
- **Scene listings** on the :ref:`test scenes <test-scenes>` page are included
  straight from the generated files, so they can't drift from the scenes.

Checks on every pull request
----------------------------

Each pull request into ``develop`` or ``main`` runs these jobs:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Job
     - What it checks
     - Blocks merge
   * - ``tests``
     - Runs pytest twice: on Python 3.11 with the oldest supported
       ``usd-core``, and on Python 3.14 with the latest.
     - Yes
   * - ``docs``
     - Builds the HTML with warnings treated as errors, so a broken
       cross-reference fails the build. Then runs the doctests and generates
       the :ref:`output for AI tools <llms-txt>`.
     - Yes
   * - ``vale``
     - Lints the docs, README, and docstrings for style and spelling.
       A spelling error fails the job.
     - Yes
   * - ``linkcheck``
     - Checks that external links still work.
     - No

``linkcheck`` doesn't block pull requests, because an outside site can be down
for reasons unrelated to the change. A scheduled run every Monday must pass
instead.

Style and spelling
------------------

Vale checks prose against the ``Vale`` and ``Google`` styles. A project
vocabulary adds USD terms, such as ``prim`` and ``Xform``, so they aren't
reported as misspellings.

To see the check in action, `pull request #5`_ added a deliberate typo.
The ``vale`` job failed on it, then passed after the fix.

.. _pull request #5: https://github.com/chad-brotherton/rst-sphinx-ci/pull/5

Publishing
----------

``main`` is protected: changes arrive only by pull request, and the
``tests``, ``docs``, and ``vale`` jobs must pass first. Each merge into
``main`` builds the site again and deploys it to GitHub Pages.

Build the docs yourself
-----------------------

Install the package with the docs and test extras, then build:

.. code-block:: console

   $ pip install -e ".[docs,test]"
   $ sphinx-build -W -b html docs/source docs/build/html
   $ sphinx-build -b doctest docs/source docs/build/doctest
   $ pytest

Open ``docs/build/html/index.html`` in a browser to read the result.

.. _llms-txt:

Output for AI tools
-------------------

Each release also publishes the docs in forms that AI tools and coding
assistants can read without parsing HTML. After the HTML build,
``scripts/build_llms_txt.py`` reads the built site and writes three kinds of
files next to the pages:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Contents
   * - ``llms.txt``
     - An index of the docs in the format described at `llmstxt.org
       <https://llmstxt.org/>`_: the
       project name, a one-line summary, and a link to each page, grouped by
       the sections of the table of contents. The pipeline page, this page, is
       listed under ``Optional``, because it doesn't help you use the tool.
   * - ``PAGE.html.md``
     - A Markdown copy of each page, such as ``overview.html.md``. The links
       in ``llms.txt`` point to these copies.
   * - ``llms-full.txt``
     - Every page's Markdown in one file, in table-of-contents order, with
       each page's URL under its title.

The script takes the page order and section names from the table of contents
on the built index page, and each page's URL from its canonical link, which
Sphinx adds because ``html_baseurl`` is set in ``conf.py``. Nothing is listed
by hand, so a new page appears in ``llms.txt`` as soon as it's in the table of
contents.

A pytest test builds the docs, runs the script, and checks that every page is
listed and converted. It also checks that no navigation or heading anchors are
left in the Markdown. The ``docs`` job also runs the script on every pull request.

On the published site, the index is at
``https://chad-brotherton.github.io/rst-sphinx-ci/llms.txt``.

To generate the files locally, build the HTML first:

.. code-block:: console

   $ sphinx-build -W -b html docs/source docs/build/html
   $ python scripts/build_llms_txt.py

.. _rst-features:

reStructuredText features in these docs
---------------------------------------

These docs use the features below. Each row links to a page that uses the
feature, so you can compare the source with the result. To see a page's
source, open it in the repository's ``docs/source/`` folder.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Feature
     - Where to see it
   * - ``toctree`` navigation
     - The left sidebar, built from the ``toctree`` directives in
       ``index.rst``.
   * - Section labels and ``:ref:``
     - Links to :ref:`cli-check` and :ref:`test-scenes`.
   * - ``:doc:`` links
     - The "Next steps" lists on :doc:`overview` and :doc:`quickstart`.
   * - Glossary and ``:term:``
     - The :doc:`glossary`, and term links throughout :doc:`overview`.
   * - Python roles such as ``:py:func:``
     - Links to :py:func:`usd_inspect.open_stage` and other API entries.
   * - ``note`` admonition
     - The Python version note on :doc:`installation`.
   * - ``tip`` admonition
     - The exit status tip on :doc:`cli`.
   * - ``important`` admonition
     - The note about editing scenes by hand, on :doc:`scenes`.
   * - ``warning`` admonition
     - What ``--check`` doesn't cover, on :doc:`overview`.
   * - ``sphinx-design`` tabs
     - The macOS, Linux, and Windows steps on :doc:`installation`.
   * - ``doctest`` blocks
     - Every example on :doc:`quickstart`.
   * - ``autodoc`` and ``automodule``
     - The :doc:`api`.
   * - ``code-block`` with a language
     - The ``bash`` and ``powershell`` blocks on :doc:`installation`, and the
       ``console`` blocks on :doc:`cli`.
   * - ``literalinclude``
     - The scene listings on :doc:`scenes`, with highlighted lines in
       ``broken_layout.usda``.
   * - ``list-table``
     - The exit status table on :doc:`cli` and the tables on this page.
   * - Definition lists
     - The options list on :doc:`cli`.
