# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import nodriver as uc

from bs4 import BeautifulSoup

from .Listing import Listing, NotFoundError


class DiscordBotsGg(Listing):
    name: str = "Discord.bots.gg"

    def __init__(self, browser: uc.Browser, application_id: int):
        super().__init__(browser)
        self.application_id = application_id

    async def fetch_raw_description(self):
        url = f"https://discord.bots.gg/bots/{self.application_id}"
        page = await self.browser.get(url)
        if (
            len(
                await page.query_selector_all(
                    ".error__title",
                )
            )
            != 0
        ):
            raise NotFoundError("Listing not found")
        description = await page.select(".bot__description")
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        return self.normalize_soup(soup).replace("’", "'")
