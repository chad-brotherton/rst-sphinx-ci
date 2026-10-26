Overview
========

USD Scene Inspector reads a USD scene file and tells you what's in it and
what's broken. It's a small Python library with a command-line tool,
``usd-inspect``, built on Pixar's open-source ``usd-core`` package.

What it does
------------

With USD Scene Inspector, you can:

- List every :term:`prim` in a scene, with its :term:`prim path` and
  :term:`schema type`.
- List the :term:`attributes <attribute>` :term:`authored` on a prim, with
  their types and values.
- Find each :term:`reference` and :term:`payload` whose target file is
  missing.

You can do each of these from the command line or from Python:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Task
     - Command line
     - Python
   * - List prims
     - ``usd-inspect FILE``
     - :py:func:`~usd_inspect.list_prims`
   * - List a prim's attributes
     - ``usd-inspect FILE --prim PATH``
     - :py:func:`~usd_inspect.list_attributes`
   * - Find missing files
     - ``usd-inspect FILE --check``
     - :py:func:`~usd_inspect.find_missing_assets`

When to use it
--------------

A USD scene often pulls in many other files through
:term:`composition arcs <composition arc>`. If one of those files is moved or
renamed, USD still opens the scene: it prints a warning and leaves out the
missing content. That makes broken references easy to miss.

Use ``usd-inspect --check`` to catch them. It exits with status 1 when a file
is missing, so you can run it in a script or CI job before you hand a scene to
someone else.

What it doesn't check
---------------------

.. warning::

   ``--check`` and :py:func:`~usd_inspect.find_missing_assets` only check
   that the files named by references and payloads exist. They don't report:

   - A sublayer that's missing.
   - A path to a file stored in an attribute, such as a texture.
   - A reference whose file exists but doesn't contain the prim it names.

   A clean result doesn't mean the scene composes exactly as you expect.

Next steps
----------

- :doc:`installation` sets up the package and the ``usd-inspect`` command.
- :doc:`quickstart` walks through each feature from Python.
- :doc:`cli` covers each command-line option.
- :doc:`glossary` defines the USD terms these docs use.
