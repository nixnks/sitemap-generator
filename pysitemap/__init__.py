import asyncio
import signal
import logging
from pysitemap.base_crawler import Crawler

logger = logging.getLogger(__name__)


def crawler(
        root_url: str,
        out_file: str = None,
        out_file_format: str = 'xml',
        max_workers=64,
        exclude_urls=None,
        http_request_options=None,
        parser=None,
        verbose: bool = False
):
    def _setup_logger():
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def _run_crawler():
        loop = asyncio.get_event_loop()
        c = Crawler(
            root_url, out_file=out_file, out_format=out_file_format, maxtasks=max_workers,
            http_request_options=http_request_options
        )

        if parser is not None:
            c.set_parser(parser_class=parser)

        if exclude_urls:
            c.set_exclude_url(urls_list=exclude_urls)

        loop.run_until_complete(c.run())

        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
        except (RuntimeError, ValueError):
            '''Except ValueError: signal only works in main thread'''
            pass

        logger.debug(f'Queue: {len(c.todo_queue)}\n'
                     f'Busy: {len(c.busy)}\n'
                     f'Done: {len(c.done)}\n'
                     f'Tasks: {len(c.tasks)}\n')

    _setup_logger()
    _run_crawler()
