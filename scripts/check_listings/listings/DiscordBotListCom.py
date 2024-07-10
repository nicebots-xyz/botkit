import nodriver as uc
import asyncio

from bs4 import BeautifulSoup

from .Listing import Listing, NotFoundError


class DiscordBotListCom(Listing):
    name: str = "DiscordBotList.com"

    def __init__(self, browser: uc.Browser, url: str):
        super().__init__(browser)
        self.url = url

    async def fetch_raw_description(self):
        page = await self.browser.get(self.url)
        try:
            await page.find("Page not found")
            raise NotFoundError("Listing not found")
        except asyncio.TimeoutError:
            pass
        description = await page.select("article > .markdown")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        soup.select_one("div").select_one("div").decompose()
        return self.normalize_soup(soup)