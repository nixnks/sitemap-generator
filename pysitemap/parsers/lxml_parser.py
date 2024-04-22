from typing import List
from lxml import etree, cssselect, html
from pysitemap.parsers.base import BaseParser


class Parser(BaseParser):
    """
    LXML based Parser
    """

    def parse(self, html_string) -> List[str]:
        doc_html = html.fromstring(html_string)
        select = cssselect.CSSSelector("a")
        return [el.get('href') for el in select(doc_html)]
