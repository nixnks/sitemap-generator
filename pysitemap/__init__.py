import asyncio
import signal
import logging
from typing import List

from pysitemap.web_crawler import WebCrawler

logger = logging.getLogger(__name__)


def crawler(
        root_url: str,
        out_file: str = None,
        out_file_format: str = 'xml',
        max_workers=64,
        exclude_urls: List[str] = None,
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
        c = WebCrawler(
            root_url, output_file=out_file, output_format=out_file_format, max_tasks=max_workers,
            http_request_options=http_request_options
        )

        if parser is not None:
            c.set_parser(parser)

        if exclude_urls:
            c.set_excluded_urls(exclude_urls)

        loop.run_until_complete(c.start_crawling())

        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
        except (RuntimeError, ValueError):
            '''Except ValueError: signal only works in main thread'''
            pass

        logger.debug(f'Current status:\n'
                     f'  Queue length: {len(c.task_queue)}\n'
                     f'  In progress tasks: {len(c.in_progress)}\n'
                     f'  Completed tasks: {len(c.completed)}\n'
                     f'  Total tasks: {len(c.tasks)}\n')

    _setup_logger()
    _run_crawler()
