import nodriver as uc
import asyncio

from bs4 import BeautifulSoup

from .Listing import Listing, NotFoundError


class DiscordMe(Listing):
    name: str = "Discord.me"

    def __init__(self, browser: uc.Browser, url: str):
        super().__init__(browser)
        self.url = url

    async def fetch_raw_description(self):
        page = await self.browser.get(self.url)
        try:
            await page.find("Sorry, the page you are looking for could not be found.")
            raise NotFoundError("Listing not found")
        except asyncio.TimeoutError:
            pass
        description = await page.select(".server-sidebar > p")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        text = self.normalize_soup(soup)
        if not text:
            raise NotFoundError("Listing not found")
        return text
