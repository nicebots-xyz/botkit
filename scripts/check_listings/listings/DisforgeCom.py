import nodriver as uc

from bs4 import BeautifulSoup
from asyncio import TimeoutError

from .Listing import Listing, NotFoundError


class DisforgeCom(Listing):
    name: str = "Disforge.com"

    def __init__(self, browser: uc.Browser, url: str):
        super().__init__(browser)
        self.url = url

    async def fetch_raw_description(self):
        page = await self.browser.get(self.url)
        # if the window location is homepage, then the bot is not found
        if len(await page.find_elements_by_text("Add this bot", tag_hint="a")) == 0:
            raise NotFoundError("Listing not found")
        description = await page.select(".card-body")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        text = self.normalize_soup(soup)
        if not text:
            raise NotFoundError("Listing not found")
        return text
