# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import nodriver as uc

from bs4 import BeautifulSoup

from .Listing import Listing


class WumpusStore(Listing):
    name: str = "Wumpus.store"

    def __init__(self, browser: uc.Browser, application_id: int):
        super().__init__(browser)
        self.application_id = application_id

    async def fetch_raw_description(self):
        url = f"https://wumpus.store/bot/{self.application_id}"
        page = await self.browser.get(url)
        description = await page.select(".css-2yutdr")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        soup.select_one("div").select_one("div").decompose()
        return self.normalize_soup(soup)
