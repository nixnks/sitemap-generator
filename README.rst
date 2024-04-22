nix-sitemap-generator
=====================

Sitemap generator library for python. Fork from *https://github.com/Haikson/sitemap-generator*.

Installing
----------
::

    pip install nix-sitemap-generator

Usage
-----

1. Import `crawler` from `pysitemap`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    from pysitemap import crawler

2. Call `crawler()`
~~~~~~~~~~~~~~~~~~~
::

    crawler(
        'https//site.com', out_file='debug/sitemap.xml', exclude_urls=[".pdf", ".jpg", ".zip"],
        http_request_options={"ssl": False}, parser=Parser
    )

Example
-------
::

    import sys
    import logging
    from pysitemap import crawler
    from pysitemap.parsers.lxml_parser import Parser

    if __name__ == '__main__':
        if '--iocp' in sys.argv:
            from asyncio import events, windows_events
            sys.argv.remove('--iocp')
            logging.info('using iocp')
            el = windows_events.ProactorEventLoop()
            events.set_event_loop(el)

        # root_url = sys.argv[1]
        root_url = 'https://www.haikson.com'
        crawler(
            root_url, out_file='debug/sitemap.xml', exclude_urls=[".pdf", ".jpg", ".zip"],
            http_request_options={"ssl": False}, parser=Parser
        )
