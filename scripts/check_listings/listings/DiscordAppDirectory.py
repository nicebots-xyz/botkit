import nodriver as uc

from bs4 import BeautifulSoup

from .Listing import Listing


class DiscordAppDirectory(Listing):
    name: str = "Discord App Directory"

    def __init__(self, browser: uc.Browser, application_id: int):
        super().__init__(browser)
        self.application_id = application_id

    async def fetch_raw_description(self):
        url = f"https://discord.com/application-directory/{self.application_id}"
        page = await self.browser.get(url)
        description = await page.select(".detailedDescription_a1eac2", timeout=25)
        html = await description.get_html()
        soup = BeautifulSoup(html, "html.parser")
        return self.normalize_soup(soup)
