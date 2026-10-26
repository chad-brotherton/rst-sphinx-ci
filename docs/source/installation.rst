Installation
============

Install USD Scene Inspector from a clone of the repository into a virtual
environment.

.. note::

   USD Scene Inspector needs Python 3.11 or later. It depends on Pixar's
   ``usd-core`` package, which publishes wheels for Python 3.11 through 3.14
   on macOS, Linux, and Windows.

Clone the repository:

.. code-block:: bash

   git clone https://github.com/chad-brotherton/rst-sphinx-ci.git
   cd rst-sphinx-ci

Create and activate a virtual environment, then install the package:

.. tab-set::
   :sync-group: os

   .. tab-item:: macOS and Linux
      :sync: unix

      .. code-block:: bash

         python3 -m venv .venv
         source .venv/bin/activate
         pip install -e .

   .. tab-item:: Windows
      :sync: windows

      .. code-block:: powershell

         py -m venv .venv
         .venv\Scripts\Activate.ps1
         pip install -e .
