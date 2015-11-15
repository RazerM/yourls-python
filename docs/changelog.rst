Change Log
==========

`Unreleased <https://github.com/RazerM/yourls-python/compare/1.1.1...HEAD>`__
-----------------------------------------------------------------------------

N/A

[1.1.1]
-------

Fixed
~~~~~

-  Fixed CLI on Python 2 due to incorrect use of ``ConfigParser``.
-  Incorrect ``ConfigParser`` import.

`1.1.0 <https://github.com/RazerM/yourls-python/compare/1.0.1...1.1.0>`__
-------------------------------------------------------------------------

Added
~~~~~

-  `Command line
   interface <http://yourls-python.readthedocs.org/en/latest/cli.html>`__.
-  Documentation section on exception handling.

Changed
~~~~~~~

-  Rename ``yourls.api`` sub-module to ``yourls.data``.
-  Rename ``yourls.exc`` sub-module to ``yourls.exceptions``. Users
   should be importing directly from ``yourls`` anyway.

`1.0.1 <https://github.com/RazerM/yourls-python/compare/1.0.0...1.0.1>`__ - 2015-11-01
--------------------------------------------------------------------------------------

Added
~~~~~

-  Added usage page to documentation.

Changed
~~~~~~~

-  Split ``YOURLSClient`` class into ``YOURLSClientBase`` and
   ``YOURLSAPIMixin`` to make it easier to re-use.
-  Refactored the code for clarity.

`1.0.0 <https://github.com/RazerM/yourls-python/compare/0ef60c1cef3979df819c8f7c0819f1ca052368f6...1.0.0>`__ - 2015-11-01
-------------------------------------------------------------------------------------------------------------------------

First release.
