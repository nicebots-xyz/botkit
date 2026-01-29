# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


import nodriver as uc
from bs4 import BeautifulSoup

from .Listing import Listing, NotFoundError


class DiscordMe(Listing):
    name: str = "Discord.me"

    def __init__(self, browser: uc.Browser, url: str) -> None:
        super().__init__(browser)
        self.url = url

    async def fetch_raw_description(self) -> str:
        page = await self.browser.get(self.url)
        try:
            await page.find("Sorry, the page you are looking for could not be found.")
            raise NotFoundError("Listing not found")
        except TimeoutError:
            pass
        description = await page.select(".server-sidebar > p")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        text = self.normalize_soup(soup)
        if not text:
            raise NotFoundError("Listing not found")
        return text
