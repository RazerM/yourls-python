# coding: utf-8
from __future__ import absolute_import, division, print_function

import os.path
import shutil
import sys
import textwrap
from contextlib import contextmanager

import click
import requests
from yourls import YOURLSAPIError, YOURLSClient, YOURLSURLExistsError

"""yourls

Usage:
  yourls shorten <url> [--keyword <keyword> --title <title>]
  yourls expand <shorturl>
  yourls url-stats <shorturl>
  yourls stats <filter> <limit> [--start <start>]
  yourls db-stats

Options:
  -k <keyword>, --keyword <keyword>
  -t <title>, --title <title>
  -s <start>, --start <start>  Filter start number
"""

if sys.version_info >= (3, 2):
    from configparser import ConfigParser, NoOptionError, NoSectionError
else:
    try:
        from ConfigParser import (
            SafeConfigParser as ConfigParser, NoOptionError, NoSectionError)
    except ImportError:
        from configparser import (
            SafeConfigParser as ConfigParser, NoOptionError, NoSectionError)


config = ConfigParser()
config_paths = ['.yourls', os.path.expanduser('~/.yourls')]
config.read(config_paths)


def config_value(name):
    """Return callable that returns config value if it exists."""
    def get():
        try:
            return config.get('yourls', name)
        except (NoOptionError, NoSectionError):
            return None
    return get


@contextmanager
def catch_exceptions():
    try:
        yield
    except (YOURLSAPIError, requests.RequestException) as exc:
        error_msg = exc.args[0]
        # Prevent duplicate "Error: ", because Click adds it too.
        error_msg = error_msg.replace('Error: ', '')
        raise click.ClickException(error_msg)


def format_shorturl(shorturl):
    title = shorturl.title.replace('"', r'\"')

    fstring = textwrap.dedent(u"""
    {s.shorturl}
      url:    {url}
      title:  {title}
      date:   {s.date!s}
      IP:     {s.ip}
      clicks: {s.clicks}
    """).strip()

    try:
        terminal_size = shutil.get_terminal_size(fallback=(80, 20))
        columns = terminal_size.columns
    except AttributeError:
        columns = 80

    indent = len('  clicks: ')  # longest row
    width = columns - indent
    textwrapper = textwrap.TextWrapper(
        width=width, initial_indent='', subsequent_indent=' ' * indent)
    url = textwrapper.fill(shorturl.url)
    title = textwrapper.fill(shorturl.title)

    return fstring.format(s=shorturl, url=url, title=title)


def format_dbstats(dbstats):
    fstring = u'{s.total_clicks} total clicks, {s.total_links} total links'
    return fstring.format(s=dbstats)


@click.group()
@click.option('--apiurl', default=config_value('apiurl'))
@click.option('--signature', default=config_value('signature'))
@click.option('--username', default=config_value('username'))
@click.option('--password', default=config_value('password'))
@click.pass_context
def cli(ctx, apiurl, signature, username, password):
    """Command line interface for YOURLS.

    Configuration parameters can be passed as switches or stored in .yourls or
    ~/.yourls.

    If your YOURLS server requires authentication, please provide one of the
    following:

    \b
    • apiurl and signature
    • apiurl, username, and password

    Configuration file format:

    \b
    [yourls]
    apiurl = http://example.com/yourls-api.php
    signature = abcdefghij
    """
    if apiurl is None:
        raise click.UsageError("apiurl missing. See 'yourls --help'")

    auth_params = dict(signature=signature, username=username, password=password)

    try:
        ctx.obj = YOURLSClient(apiurl=apiurl, **auth_params)
    except TypeError:
        raise click.UsageError("authentication paremeters overspecified. "
                               "See 'yourls --help'")


@cli.command()
@click.argument('url')
@click.option('--keyword', '-k')
@click.option('--title', '-t')
@click.option('--only-new/--allow-existing', default=False,
              help="Exit with error if URL has already been shortened. "
                   "(Default: allow existing)")
@click.option('--simple', '-s', is_flag=True,
              help='Print short URL instead of full ShortenedURL object')
@click.pass_obj
def shorten(yourls, url, keyword, title, only_new, simple):
    new = True
    try:
        shorturl = yourls.shorten(url, keyword=keyword, title=title)
    except YOURLSURLExistsError as exc:
        shorturl = exc.url
        new = False
        if only_new:
            raise click.ClickException(exc.args[0])
    except (YOURLSAPIError, requests.RequestException) as exc:
        raise click.ClickException(exc.args[0])

    if simple:
        linkstr = shorturl.shorturl
    else:
        linkstr = format_shorturl(shorturl)

    if only_new:
        status = ''
    else:
        status = u'New: ' if new else u'Exists: '

    click.echo(u'{status}{linkstr}'.format(status=status, linkstr=linkstr))


@cli.command()
@click.argument('shorturl')
@click.pass_obj
def expand(yourls, shorturl):
    with catch_exceptions():
        longurl = yourls.expand(shorturl)
    click.echo(longurl)


@cli.command('url-stats')
@click.argument('shorturl')
@click.pass_obj
def url_stats(yourls, shorturl):
    with catch_exceptions():
        shorturl = yourls.url_stats(shorturl)

    linkstr = format_shorturl(shorturl)
    click.echo(linkstr)


@cli.command(help="Filter links by 'top', 'bottom', 'rand', or 'last'")
@click.argument('filter', type=click.Choice(('top', 'bottom', 'rand', 'last')))
@click.argument('limit', type=int)
@click.option('--start', '-b', type=int)
@click.option('--simple', '-s', is_flag=True,
              help='Print short URLs instead of full ShortenedURL objects')
@click.pass_obj
def stats(yourls, filter, limit, start, simple):
    with catch_exceptions():
        links, stats = yourls.stats(filter=filter, limit=limit, start=start)
    click.echo(format_dbstats(stats))
    for link in links:
        if simple:
            linkstr = link.shorturl
        else:
            linkstr = format_shorturl(link)
        click.echo(linkstr)


@cli.command('db-stats')
@click.pass_obj
def db_stats(yourls):
    with catch_exceptions():
        stats = yourls.db_stats()
    click.echo(format_dbstats(stats))


def main():
    cli(prog_name='yourls')

if __name__ == '__main__':
    main()
