yourls
------

|PyPI Version| |Documentation| |Travis| |Coverage| |Python Version| |MIT License|

Installation
~~~~~~~~~~~~

.. code:: bash

    $ pip install yourls

Example
~~~~~~~

.. code:: python

   >>> from yourls import YOURLSClient

   >>> yourls = YOURLSClient('http://example.com/yourls-api.php', signature='6f344c2a8p')
   >>> yourls.shorten('http://google.com')
   ShortenedURL(
       shorturl='http://example.com/abcde',
       url='http://google.com',
       title='Google',
       date=datetime.datetime(2015, 10, 31, 14, 31, 4),
       ip='203.0.113.0',
       clicks=0,
       keyword='abcde')

Documentation
~~~~~~~~~~~~~

For in-depth information, `visit the
documentation <http://yourls-python.readthedocs.org/en/latest/>`__!

.. |Travis| image:: http://img.shields.io/travis/RazerM/yourls-python/master.svg?style=flat-square&label=travis
   :target: https://travis-ci.org/RazerM/yourls-python
.. |PyPI Version| image:: http://img.shields.io/pypi/v/yourls.svg?style=flat-square
   :target: https://pypi.python.org/pypi/yourls/
.. |Python Version| image:: https://img.shields.io/badge/python-2.7%2C%203-brightgreen.svg?style=flat-square
   :target: https://www.python.org/downloads/
.. |MIT License| image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
   :target: https://raw.githubusercontent.com/RazerM/yourls-python/master/LICENSE
.. |Coverage| image:: https://img.shields.io/codecov/c/github/RazerM/yourls-python/master.svg?style=flat-square
   :target: https://codecov.io/github/RazerM/yourls-python?branch=master
.. |Documentation| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square
   :target: http://yourls-python.readthedocs.org/en/latest/
