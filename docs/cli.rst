**********************
Command Line Interface
**********************

You can invoke ``yourls`` or ``python -m yourls`` on the command line.

.. code-block:: bash

   $ yourls
   Usage: yourls [OPTIONS] COMMAND [ARGS]...

     Command line interface for YOURLS.

     Configuration parameters can be passed as switches or stored in .yourls or
     ~/.yourls.

     Please provide one of the following:
     • apiurl and signature
     • apiurl, username, and password

     Configuration file format:

     [yourls]
     apiurl = http://example.com/yourls-api.php
     signature = abcdefghij

   Options:
     --apiurl TEXT
     --signature TEXT
     --username TEXT
     --password TEXT
     --help            Show this message and exit.

   Commands:
     db-stats
     expand
     shorten
     stats
     url-stats

You can see help for individual commands: ``yourls shorten --help`` etc.
