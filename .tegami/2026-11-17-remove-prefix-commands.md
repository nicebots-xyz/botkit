---
packages:
  botkit: minor
---

## Remove prefix and bridge commands

Botkit now runs on a plain `discord.Bot` and only supports application commands. The `bot.prefix` setting is gone and is ignored if still present, and the bot never requests the `message_content` intent.

Breaking changes for extensions:

- `custom.ExtContext` and the `custom.Context` alias are removed, use `custom.ApplicationContext`.
- `custom.ApplicationContext` extends `discord.ApplicationContext` instead of `bridge.BridgeApplicationContext`.
- `CooldownExceeded` extends `discord.CheckFailure` instead of `commands.CheckFailure`.
- `nice_errors` no longer listens to `on_command_error`.
- Cogs should extend `discord.Cog` instead of `commands.Cog`.
