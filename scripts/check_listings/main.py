# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import asyncio
import nodriver as uc
import markdown
import argparse
import yaml

from termcolor import cprint
from bs4 import BeautifulSoup

from .listings import (
    normalize_soup,
    TopGg,
    DiscordsCom,
    WumpusStore,
    DiscordAppDirectory,
    DiscordBotListCom,
    DisforgeCom,
    DiscordBotsGg,
    DiscordMe,
    NotFoundError,
)

COMPLETED = False


async def async_main(args):
    with open("description.md", "r", encoding="utf-8") as f:
        description: str = f.read()
    with open(args.config, "r", encoding="utf-8") as f:
        config: dict = yaml.safe_load(f)
    application_id = (
        args.application_id if args.application_id else config["application_id"]
    )

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
        except asyncio.TimeoutError:
            cprint(f"{listing.name} timed out")
            continue
        if description == its_description:
            cprint(f"{listing.name} matches", "black", "on_green")
        else:
            cprint(f"{listing.name} does not match", "black", "on_yellow")
    global COMPLETED
    COMPLETED = True


def main():
    parser = argparse.ArgumentParser(
        prog="Listings checker",
        description="Check the published status of your discord listings",
    )
    parser.add_argument("-i", "--application_id", required=False, default=None)
    parser.add_argument("-c", "--config", required=False, default="listings.yaml")

    args = parser.parse_args()
    try:
        asyncio.get_event_loop().run_until_complete(async_main(args))
    except Exception as e:  # noqa
        if not COMPLETED:
            raise


if __name__ == "__main__":
    main()
