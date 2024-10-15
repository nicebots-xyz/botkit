# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import nodriver as uc

from bs4 import BeautifulSoup

from .Listing import Listing, NotFoundError


class TopGg(Listing):
    name: str = "Top.gg"

    def __init__(self, browser: uc.Browser, application_id: int):
        super().__init__(browser)
        self.application_id = application_id

    async def fetch_raw_description(self):
        url = f"https://top.gg/bot/{self.application_id}"
        page = await self.browser.get(url)
        if (
            len(
                await page.find_elements_by_text(
                    "Oops! We can’t seem to find the page you’re looking for.",
                    tag_hint="p",
                )
            )
            != 0
        ):
            raise NotFoundError("bot was not found")
        description = await page.select(".entity-content__description")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        return self.normalize_soup(soup)
