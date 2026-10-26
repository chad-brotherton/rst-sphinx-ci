.. _glossary:

Glossary
========

These are the USD terms the docs use. Other pages link to the definitions here.

.. glossary::
   :sorted:

   asset path
      A path to a file, written in a scene, such as the target of a :term:`reference`
      or :term:`payload`. In a ``.usda`` file, asset paths are wrapped in ``@``
      signs, like ``@./props/crate.usda@``. USD resolves a relative asset path
      against the :term:`layer` that contains it, not against your current
      folder.

   attribute
      A named, typed value on a :term:`prim`, such as a sphere's ``radius``.
      ``usd-inspect --prim`` lists a prim's :term:`authored` attributes.

   authored
      Written in a :term:`layer`. An attribute that isn't authored still has a
      value: the fallback that its prim's :term:`schema type` defines.
      USD Scene Inspector lists only authored attributes.

   composition arc
      A link that tells USD to combine scene description from somewhere else
      into a :term:`prim`. A :term:`reference` and a :term:`payload` are both
      composition arcs. USD has other kinds too, such as sublayers and
      variants, which USD Scene Inspector doesn't check.

   default prim
      The :term:`prim` that a :term:`layer` names as its entry point. When
      another file references the layer without naming a prim, USD uses the
      default prim.

   layer
      One file of scene description, such as a ``.usda`` file. A
      :term:`stage` is built from one or more layers.

   payload
      A :term:`composition arc` that works like a :term:`reference`, but that
      you can leave unloaded. Payloads let you open a large scene without
      reading every file it points to. :py:func:`usd_inspect.open_stage` loads
      all payloads.

   prim
      An element in a scene's hierarchy, such as a transform, a cube, or a
      sphere. Each prim has a :term:`prim path` and usually a
      :term:`schema type`.

   prim path
      The location of a :term:`prim` in the hierarchy, written with slashes,
      like ``/World/Ball``. A prim path that starts with ``/`` is absolute.

   reference
      A :term:`composition arc` that brings a :term:`prim` from another
      :term:`layer` into the scene, at the location of the prim that has the
      reference. If the target file can't be found, USD warns and the prim
      composes without that content.

   schema type
      The kind of a :term:`prim`, such as ``Xform``, ``Cube``, or ``Sphere``.
      The schema type decides which attributes the prim supports and their
      fallback values.

   stage
      The composed scene: the layer you opened plus every layer it pulls in
      through composition arcs. :py:func:`usd_inspect.open_stage` returns a
      stage.
