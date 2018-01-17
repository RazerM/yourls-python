Change Log
==========

.. _unreleasedunreleased:

`Unreleased <https://github.com/RazerM/yourls-python/compare/1.2.3...HEAD>`__
-----------------------------------------------------------------------------

N/A

`1.2.3 <https://github.com/RazerM/yourls-python/compare/1.2.2...1.2.3>`__
-------------------------------------------------------------------------

Fixed
~~~~~

-  ``yourls`` can be installed with setuptools v38.0+, which requires
   ``install_requires`` in ``setup.py`` to be ordered.

.. _section-1:

`1.2.2 <https://github.com/RazerM/yourls-python/compare/1.2.1...1.2.2>`__ - 2016-01-29
--------------------------------------------------------------------------------------

.. _fixed-1:

Fixed
~~~~~

-  Exceptions used incorrect ``super()`` calls.
-  Conditional dependencies now work with wheel format.

.. _section-2:

`1.2.1 <https://github.com/RazerM/yourls-python/compare/1.2.0...1.2.1>`__ - 2015-11-24
--------------------------------------------------------------------------------------

.. _fixed-2:

Fixed
~~~~~

-  Unicode handling on Python 2 in CLI.

.. _section-3:

`1.2.0 <https://github.com/RazerM/yourls-python/compare/1.1.1...1.2.0>`__ - 2015-11-16
--------------------------------------------------------------------------------------

Changed
~~~~~~~

-  Nicer CLI output for ``ShortenedURL`` and ``DBStats`` objects.

.. _fixed-3:

Fixed
~~~~~

-  ``NoSectionError`` with blank configuration file
   (`#2 <https://github.com/RazerM/yourls-python/issues/2>`__)
-  Short option for ``--start`` when calling ``yourls stats`` changed to
   ``-b`` to prevent conflict with ``-s`` for ``--simple``
   (`#1 <https://github.com/RazerM/yourls-python/issues/1>`__).

.. _section-4:

`1.1.1 <https://github.com/RazerM/yourls-python/compare/1.1.0...1.1.1>`__ - 2015-11-15
--------------------------------------------------------------------------------------

.. _fixed-4:

Fixed
~~~~~

-  Fixed CLI on Python 2 due to incorrect use of ``ConfigParser``.
-  Incorrect ``ConfigParser`` import.

.. _section-5:

`1.1.0 <https://github.com/RazerM/yourls-python/compare/1.0.1...1.1.0>`__ - 2015-11-15
--------------------------------------------------------------------------------------

Added
~~~~~

-  `Command line
   interface <http://yourls-python.readthedocs.org/en/latest/cli.html>`__.
-  Documentation section on exception handling.

.. _changed-1:

Changed
~~~~~~~

-  Rename ``yourls.api`` sub-module to ``yourls.data``.
-  Rename ``yourls.exc`` sub-module to ``yourls.exceptions``. Users
   should be importing directly from ``yourls`` anyway.

.. _section-6:

`1.0.1 <https://github.com/RazerM/yourls-python/compare/1.0.0...1.0.1>`__ - 2015-11-01
--------------------------------------------------------------------------------------

.. _added-1:

Added
~~~~~

-  Added usage page to documentation.

.. _changed-2:

Changed
~~~~~~~

-  Split ``YOURLSClient`` class into ``YOURLSClientBase`` and
   ``YOURLSAPIMixin`` to make it easier to re-use.
-  Refactored the code for clarity.

.. _section-7:

`1.0.0 <https://github.com/RazerM/yourls-python/compare/01e4bf7b77738eaca1246e238266887e009e0dbb...1.0.0>`__ - 2015-11-01
-------------------------------------------------------------------------------------------------------------------------

First release.
