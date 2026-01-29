# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 NiceBots.xyz


from tortoise import fields
from tortoise.models import Model


class Guild(Model):
    """User model.

    Represents a user in the database.

    Attributes
    ----------
        id (int): Discord user ID.
        free_credits (int): Amount of free credits the user has.
        premium_credits (int): Amount of premium credits the user has.

    """

    id: fields.Field[int] = fields.BigIntField(pk=True)


__all__ = ["Guild"]
