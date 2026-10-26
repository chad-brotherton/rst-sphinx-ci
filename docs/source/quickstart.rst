Quick start
===========

This page walks you through inspecting your first scene from Python. You open
a scene, list its prims, read a prim's attributes, and check for missing
files.

Before you start, install USD Scene Inspector. See :doc:`installation`.

The examples use the test scenes in ``examples/scenes/`` in the repository.
``SCENES`` is the path to that folder.

Open a scene
------------

Open a file with :py:func:`usd_inspect.open_stage`. It returns a USD stage, the
object that holds the composed scene:

.. doctest::

   >>> from usd_inspect import open_stage
   >>> stage = open_stage(SCENES / "simple.usda")
   >>> stage.GetDefaultPrim().GetPath()
   Sdf.Path('/World')

If the file doesn't exist, ``open_stage`` raises :py:exc:`FileNotFoundError`.

List the prims
--------------

Call :py:func:`usd_inspect.list_prims` to get each prim's path and type:

.. doctest::

   >>> from usd_inspect import list_prims
   >>> for prim in list_prims(stage):
   ...     print(prim.path, prim.type_name)
   /World Xform
   /World/Box Cube
   /World/Ball Sphere

Read a prim's attributes
------------------------

Pass a prim path to :py:func:`usd_inspect.list_attributes` to see the
attributes set on that prim:

.. doctest::

   >>> from usd_inspect import list_attributes
   >>> for attr in list_attributes(stage, "/World/Ball"):
   ...     print(attr.name, attr.value)
   radius 1.0
   userProperties:label bouncy ball
   xformOp:translate (3, 0, 1)
   xformOpOrder [xformOp:translate]

Only attributes written in the scene appear. Attributes that keep their schema
default, such as a sphere's ``visibility``, don't.

Check for missing files
-----------------------

A scene can pull in other files through references and payloads. Call
:py:func:`usd_inspect.find_missing_assets` to find the ones whose files
can't be found:

.. doctest::

   >>> from usd_inspect import find_missing_assets
   >>> broken = open_stage(SCENES / "broken_layout.usda")
   >>> for missing in find_missing_assets(broken):
   ...     print(missing.prim_path, missing.arc, missing.asset_path)
   /World/MissingCrate reference ./props/missing_crate.usda
   /World/MissingPayload payload ./props/missing_payload.usda

An empty list means every file was found:

.. doctest::

   >>> find_missing_assets(stage)
   []

.. tip::

   USD also prints a warning for each missing file when it opens the scene.
   ``find_missing_assets`` gives you the same information as data you can
   check in a script.

Next steps
----------

- See :doc:`api` for every function and the fields each result has.
