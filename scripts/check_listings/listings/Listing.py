import nodriver as uc
import re

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseError(Exception):
    pass


class NotFoundError(BaseError):
    pass


class Listing(ABC):
    """
    Represents a Discord Bot listing website
    """

    def __init__(self, browser: uc.Browser, *args, **kwargs):
        self.browser = browser

    def normalize_soup(self, soup: BeautifulSoup) -> str:
        """
        Normalize the text from a BeautifulSoup object
        """
        return re.sub(
            r"\n{2,}", "\n", soup.get_text(separator="\n", strip=True).strip()
        ).strip()

    @abstractmethod
    async def fetch_raw_description(self) -> str:
        """
        Fetch the raw description of the bot from the website

        :raises NotFoundError: If the bot is not found
        :return: The raw description of the bot
        """
        pass
