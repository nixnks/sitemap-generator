import re
from typing import List

from pysitemap.parsers.base import BaseParser


class Parser(BaseParser):
    """
        Parser based on regular expressions
    """

    def parse(self, html_string) -> List[str]:
        return re.findall(r'(?i)href\s*?=\s*?[\"\']?([^\s\"\'<>]+)[\"\']', html_string)
