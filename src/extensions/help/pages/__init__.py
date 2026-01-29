# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


from itertools import chain
from pathlib import Path

import yaml

from .classes import HelpCategoryTranslation, HelpTranslation

# iterate over .y[a]ml files in the same directory as this file
categories: list[HelpCategoryTranslation] = []

for file in chain(Path(__file__).parent.glob("*.yaml"), Path(__file__).parent.glob("*.yml")):
    with open(file, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    categories.append(HelpCategoryTranslation(**data))

categories.sort(key=lambda item: item.order)

help_translation = HelpTranslation(categories=categories)
