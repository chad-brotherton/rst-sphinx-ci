.. _test-scenes:

Test scenes
===========

The examples in these docs, the doctests, and the tests all run against four
small scenes in ``examples/scenes/``. The script ``scripts/make_scenes.py``
generates them, so every scene is reproducible and free to redistribute.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - What it shows
   * - ``simple.usda``
     - A few typed prims with :term:`authored` attributes.
   * - ``props/crate.usda``
     - A small asset that other scenes reference.
   * - ``layout.usda``
     - Three crates brought in by :term:`reference` and :term:`payload`. Every
       file is found.
   * - ``broken_layout.usda``
     - One reference and one payload whose files are missing.

Regenerate the scenes
---------------------

Run the script from the root of the repository:

.. code-block:: console

   $ python scripts/make_scenes.py

The output is the same every time you run it.

.. important::

   Don't edit the ``.usda`` files by hand. A test compares each committed
   scene with a fresh run of the script and fails if they differ. To change a
   scene, change ``scripts/make_scenes.py`` and run it again.

simple.usda
-----------

A transform with a cube and a sphere. The sphere has a translation and a
custom string attribute, so :py:func:`usd_inspect.list_attributes` has several
value types to show.

.. literalinclude:: ../../examples/scenes/simple.usda
   :language: usda

props/crate.usda
----------------

A crate asset: a transform named ``Crate`` with a cube inside it. ``Crate`` is
the :term:`default prim`, so other scenes can reference the file without
naming a prim.

.. literalinclude:: ../../examples/scenes/props/crate.usda
   :language: usda

layout.usda
-----------

Three copies of the crate. ``CrateA`` and ``CrateB`` use references, and
``CrateC`` uses a payload. All three :term:`asset paths <asset path>` point to
``props/crate.usda``, which exists, so
:py:func:`usd_inspect.find_missing_assets` returns an empty list.

.. literalinclude:: ../../examples/scenes/layout.usda
   :language: usda

broken_layout.usda
------------------

One crate that resolves, plus two prims whose targets don't exist:
``MissingCrate`` references ``props/missing_crate.usda``, and
``MissingPayload`` loads ``props/missing_payload.usda`` as a payload. USD
still opens the scene. It prints a warning for each missing file and composes
those prims without the missing content.

.. literalinclude:: ../../examples/scenes/broken_layout.usda
   :language: usda
   :emphasize-lines: 15-25

To see how USD Scene Inspector reports these files, see
:ref:`cli-check` or :doc:`quickstart`.
