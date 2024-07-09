import nodriver as uc

from bs4 import BeautifulSoup
from asyncio import TimeoutError

from .Listing import Listing, NotFoundError


class DiscordsCom(Listing):
    name: str = "Discords.com"

    def __init__(self, browser: uc.Browser, application_id: int):
        super().__init__(browser)
        self.application_id = application_id

    async def fetch_raw_description(self):
        url = f"https://discords.com/bots/bot/{self.application_id}"
        page = await self.browser.get(url)
        description = await page.select("app-bot-page-description")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        text = self.normalize_soup(soup)
        if not text:
            raise NotFoundError("Listing not found")
        return text
