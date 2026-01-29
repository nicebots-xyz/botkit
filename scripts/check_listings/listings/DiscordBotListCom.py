# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


import nodriver as uc
from bs4 import BeautifulSoup

from .Listing import Listing, NotFoundError


class DiscordBotListCom(Listing):
    name: str = "DiscordBotList.com"

    def __init__(self, browser: uc.Browser, url: str) -> None:
        super().__init__(browser)
        self.url = url

    async def fetch_raw_description(self) -> str:
        page = await self.browser.get(self.url)
        try:
            await page.find("Page not found")
            raise NotFoundError("Listing not found")
        except TimeoutError:
            pass
        description = await page.select("article > .markdown")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", {"rel": "nofollow ugc"}):
            a.unwrap()
        return self.normalize_soup(soup)
