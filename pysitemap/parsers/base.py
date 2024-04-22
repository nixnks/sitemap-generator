from typing import List
from abc import ABC, abstractmethod


class BaseParser(ABC):

    @abstractmethod
    def parse(self, html_string) -> List[str]:
        """
        Base parse method
        """
