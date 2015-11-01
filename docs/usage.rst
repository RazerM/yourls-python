*****
Usage
*****

Installation
------------

.. code:: bash

    $ pip install yourls

Overview
--------

yourls is a Python client for your `YOURLS`_ server. The API is fairly simple,
and API errors are turned into Python exceptions.

.. _`YOURLS`: http://yourls.org

The main functionality is shown here:

.. code:: python

    >>> from yourls import YOURLSClient

    >>> yourls = YOURLSClient('http://example.com/yourls-api.php', signature='6f344c2a8p')
    >>> shorturl = yourls.shorten('http://google.com')
    >>> shorturl
    ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 10, 31, 14, 31, 4),
        ip='203.0.113.0',
        clicks=0,
        keyword='abcde')

    >>> yourls.expand('abcde')
    'http://google.com'
    >>> yourls.expand('http://example.com/abcde')
    'http://google.com'

    >>> yourls.url_stats('abcde')
    ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 10, 31, 14, 31, 4),
        ip='203.0.113.0',
        clicks=0,
        keyword='abcde')

    >>> links, stats = yourls.stats(filter='random', limit=2)
    >>> links
    [ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 10, 31, 14, 31, 4),
        ip='203.0.113.0',
        clicks=2,
        keyword='abcde'),
    ShortenedURL(
        shorturl='http://example.com/gd65t',
        url='http://www.youtube.com',
        title='YouTube',
        date=datetime.datetime(2015, 10, 31, 11, 34, 5),
        ip='203.0.113.0',
        clicks=567,
        keyword='gd65t')]
    >>> stats
    DBStats(total_clicks=1234, total_links=5678)

    >>> yourls.db_stats()
    DBStats(total_clicks=1234, total_links=5678)

Logging
-------

Logging is disabled by default. Let's enable the logger and set up a logbook
handler.

.. code-block:: python

    from logbook import StderrHandler
    from yourls import YOURLSClient, logger

    logger.disabled = False

    yourls = YOURLSClient('http://example.com/yourls-api.php', signature='6f344c2a8p')

    with StderrHandler():
        yourls.shorten('http://www.google.com')

Here, `logger` is an instance of :py:class:`logbook.Logger`. By default, the
level is set to :py:data:`logbook.NOTSET` (i.e. everything is logged).

In our example, we would see the following output:

.. code::

    [2015-11-01 17:15:57.899368] DEBUG: yourls: Received <Response [200]> with JSON {'message': 'http://www.google.com added to database', 'url': {'keyword': 'abcde', 'title': 'Google', 'date': '2015-11-01 17:15:57', 'url': 'http://www.google.com', 'ip': '203.0.113.0'}, 'status': 'success', 'shorturl': 'http://example.com/abcde', 'title': 'Google', 'statusCode': 200}

API Plugins
-----------

If you want to support YOURLS plugins that add API methods
(e.g. `API Delete`_), the following is the recommended way to do so.

.. code-block:: python

    from yourls import YOURLSClientBase, YOURLSAPIMixin

    class YOURLSDeleteMixin(object):
        def delete(short):
            data = dict(action='delete', shorturl=short)
            self._api_request(params=data)

    class YOURLSClient(YOURLSDeleteMixin, YOURLSAPIMixin, YOURLSClientBase):
        """YOURLS client with API delete support."""

.. _`API Delete`: https://github.com/claytondaley/yourls-api-delete

