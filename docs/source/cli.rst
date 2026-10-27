Command-line usage
==================

The ``usd-inspect`` command lists the prims in a scene, shows a prim's
attributes, and checks for missing files. It's installed with the package.
See :doc:`installation`.

The examples on this page use the test scenes in ``examples/scenes/``. Run
them from the root of the repository.

List the prims in a scene
-------------------------

Pass a file to list each prim's path and type:

.. code-block:: console

   $ usd-inspect examples/scenes/simple.usda
   /World       Xform
   /World/Box   Cube
   /World/Ball  Sphere

Show a prim's attributes
------------------------

Add ``--prim`` with a prim path to list the attributes set on that prim, with
each attribute's type and value:

.. code-block:: console

   $ usd-inspect examples/scenes/simple.usda --prim /World/Ball
   radius                double   1.0
   userProperties:label  string   bouncy ball
   xformOp:translate     double3  (3, 0, 1)
   xformOpOrder          token[]  [xformOp:translate]

Attributes that keep their schema default don't appear. A prim with no
attributes set prints a message instead:

.. code-block:: console

   $ usd-inspect examples/scenes/simple.usda --prim /World
   No authored attributes on /World.

.. _cli-check:

Check for missing files
-----------------------

Add ``--check`` to list the references and payloads whose files can't be
found. Each line shows the prim, the kind of arc, and the path written in the
scene:

.. code-block:: console

   $ usd-inspect examples/scenes/broken_layout.usda --check
   /World/MissingCrate    reference  ./props/missing_crate.usda
   /World/MissingPayload  payload    ./props/missing_payload.usda

If every file is found, the command says so:

.. code-block:: console

   $ usd-inspect examples/scenes/layout.usda --check
   No missing files.

.. tip::

   ``--check`` exits with status 1 when it finds a missing file, so you can
   use it to stop a script or CI job before a broken scene goes further.

Exit status
-----------

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Status
     - Meaning
   * - 0
     - Success. With ``--check``, no files are missing.
   * - 1
     - ``--check`` found at least one missing file.
   * - 2
     - The arguments are invalid, the file doesn't exist or isn't a USD file,
       or no prim exists at the ``--prim`` path.

Options
-------

``file``
   The ``.usda`` or ``.usd`` file to inspect.

``--prim PATH``
   List the attributes set on the prim at ``PATH``, such as ``/World/Ball``.

``--check``
   List references and payloads whose files are missing. You can't combine
   ``--check`` with ``--prim``. If you pass both, ``usd-inspect`` prints an
   error and exits with status 2.

``--version``
   Print the version and exit.

``-h``, ``--help``
   Print a summary of the options and exit.

.. note::

   USD prints a warning for each missing file when it opens a scene.
   ``usd-inspect`` hides those warnings, because ``--check`` reports the same
   files. In Python, :py:func:`usd_inspect.open_stage` doesn't hide them.

To use these features from Python instead, see :doc:`quickstart`.
