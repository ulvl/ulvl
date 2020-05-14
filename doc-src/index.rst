*************************************
Universal Level Formats documentation
*************************************

.. This file has been dedicated to the public domain, to the extent
   possible under applicable law, via CC0. See
   http://creativecommons.org/publicdomain/zero/1.0/ for more
   information. This file is offered as-is, without any warranty.

.. contents::

.. automodule:: ulvl

Level Format Classes
====================

These classes load and save levels for their respective formats.
:class:`ulvl.JSL` is generally the recommended format, but alternatives
are offered as well.

ulvl.JSL
--------

.. autoclass:: ulvl.JSL

ulvl.JSL Methods
~~~~~~~~~~~~~~~~

.. automethod:: ulvl.JSL.load

.. automethod:: ulvl.JSL.save

ulvl.ASCL
---------

.. autoclass:: ulvl.ASCL

ulvl.ASCL Methods
~~~~~~~~~~~~~~~~~

.. automethod:: ulvl.ASCL.load

.. automethod:: ulvl.ASCL.save

ulvl.ULX
--------

.. autoclass:: ulvl.ULX

ulvl.ULX Methods
~~~~~~~~~~~~~~~~

.. automethod:: ulvl.ULX.load

.. automethod:: ulvl.ULX.save

ulvl.TMX
--------

.. autoclass:: ulvl.TMX

ulvl.TMX Methods
~~~~~~~~~~~~~~~~

.. automethod:: ulvl.TMX.load

Helper Classes
==============

These classes are helpers used by the level format classes to store
data.

.. autoclass:: ulvl.TileLayer

.. autoclass:: ulvl.LevelObject

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
