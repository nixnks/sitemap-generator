import logging
import asyncio
import aiohttp
from typing import Any, Optional, MutableMapping
import urllib.parse
from pysitemap.format_processors.xml import XMLWriter
from pysitemap.format_processors.text import TextWriter
from pysitemap.parsers.re_parser import Parser as ReParser

logger = logging.getLogger(__name__)


class WebCrawler:
    def __init__(
            self, root_url: str, output_file: str, output_format: str = 'xml',
            max_tasks: int = 100, queue_backend: Any = set, completed_backend: Any = dict,
            http_request_options: Optional[MutableMapping] = None
    ):
        self.root_url = root_url
        self.task_queue = queue_backend()
        self.in_progress = set()
        self.completed = completed_backend()
        self.tasks = set()
        self.semaphore = asyncio.Semaphore(max_tasks)
        self.http_request_options = http_request_options or {}
        self.session = aiohttp.ClientSession()
        self.writer = self.get_format_processor(output_format)(output_file)
        self.parser = ReParser()
        self.excluded_urls = []

    @staticmethod
    def get_format_processor(output_format):
        format_processors = {
            'xml': XMLWriter,
            'txt': TextWriter
        }
        return format_processors.get(output_format)

    def set_parser(self, parser_class):
        self.parser = parser_class()

    def set_excluded_urls(self, urls_list):
        self.excluded_urls = urls_list

    async def start_crawling(self):
        asyncio.ensure_future(self.add_urls([(self.root_url, '')]))
        await asyncio.sleep(1)
        while self.in_progress:
            await asyncio.sleep(1)

        await self.session.close()
        await self.writer.write([key for key, value in self.completed.items() if value])

    async def add_urls(self, urls):
        for url, parent_url in urls:
            url = self.normalize_url(url, parent_url)
            if self.should_add_url(url):
                await self.add_url_to_task_queue(url)

    @staticmethod
    def normalize_url(url, parent_url):
        url = urllib.parse.urljoin(parent_url, url)
        url, _ = urllib.parse.urldefrag(url)
        return url

    def should_add_url(self, url):
        return (url.startswith(self.root_url) and
                not any(exclude_part in url for exclude_part in self.excluded_urls) and
                url not in self.in_progress and
                url not in self.completed and
                url not in self.task_queue)

    async def add_url_to_task_queue(self, url):
        self.task_queue.add(url)
        await self.semaphore.acquire()
        task = asyncio.ensure_future(self.process_url(url))
        task.add_done_callback(lambda t: self.semaphore.release())
        task.add_done_callback(self.tasks.remove)
        self.tasks.add(task)

    async def process_url(self, url):
        self.task_queue.remove(url)
        self.in_progress.add(url)
        try:
            await self.fetch_and_parse_url(url)
        except Exception as exc:
            logger.exception(exc)
            self.completed[url] = False
        finally:
            self.in_progress.remove(url)
            logger.info(
                f'Completed tasks: {len(self.completed)}, Pending tasks: {len(self.tasks)}, Queue length: {len(self.task_queue)}')

    async def fetch_and_parse_url(self, url):
        resp = await self.session.get(url, **self.http_request_options)
        if (resp.status == 200 and
                ('text/html' in resp.headers.get('content-type'))):
            data = (await resp.read()).decode('utf-8', 'replace')
            urls = self.parser.parse(html_string=data)
            asyncio.Task(self.add_urls([(u, url) for u in urls]))
        resp.close()
        self.completed[url] = True
