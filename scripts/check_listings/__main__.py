# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz

import argparse
import asyncio
from typing import Any

import markdown
import nodriver as uc
import yaml
from aiofile import async_open as open  # noqa: A004
from bs4 import BeautifulSoup
from termcolor import cprint

from .listings import (
    DiscordAppDirectory,
    DiscordBotListCom,
    DiscordBotsGg,
    DiscordMe,
    DiscordsCom,
    DisforgeCom,
    NotFoundError,
    TopGg,
    WumpusStore,
    normalize_soup,
)

completed = False


async def async_main(args: argparse.Namespace) -> None:
    async with open("description.md", encoding="utf-8") as f:
        description: str = await f.read()
    async with open(args.config, encoding="utf-8") as f:
        config: dict[Any, Any] = yaml.safe_load(await f.read())
    application_id = args.application_id or config["application_id"]

    description = markdown.markdown(description)
    description = normalize_soup(BeautifulSoup(description, "html.parser"))

    browser = await uc.start()
    listings = [
        DiscordsCom(browser, application_id),
        WumpusStore(browser, application_id),
        DiscordAppDirectory(browser, application_id),
        TopGg(browser, application_id),
        DiscordBotsGg(browser, application_id),
    ]

    if url := config.get("DiscordBotListCom", {}).get("url"):
        listings.append(DiscordBotListCom(browser, url))

    if url := config.get("DisforgeCom", {}).get("url"):
        listings.append(DisforgeCom(browser, url))

    if url := config.get("DiscordMe", {}).get("url"):
        listings.append(DiscordMe(browser, url))

    for listing in listings:
        try:
            its_description = await listing.fetch_raw_description()
        except NotFoundError:
            cprint(f"{listing.name} not published", "black", "on_light_red")
            continue
        except TimeoutError:
            cprint(f"{listing.name} timed out")
            continue
        if description == its_description:
            cprint(f"{listing.name} matches", "black", "on_green")
        else:
            cprint(f"{listing.name} does not match", "black", "on_yellow")
    global completed  # noqa: PLW0603
    completed = True


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="Listings checker",
        description="Check the published status of your discord listings",
    )
    parser.add_argument("-i", "--application_id", required=False, default=None)
    parser.add_argument("-c", "--config", required=False, default="listings.yaml")

    args = parser.parse_args()
    try:
        asyncio.get_event_loop().run_until_complete(async_main(args))
    except Exception:
        if not completed:
            raise


if __name__ == "__main__":
    main()
