<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->

# Branding Extension

The Branding extension is a background task that customizes your bot's presence. It is
**enabled** by default.

## Features

The Branding extension performs the following tasks:

- It updates the bot's status every 5 minutes by default. The status can be set to
  playing, watching, listening, streaming, or custom.

## Usage

The Branding extension is a background task and does not provide any commands for
interaction. Once properly configured, it will automatically perform its tasks without
any further intervention.

## Configuration

The Branding extension requires the following configuration:

- `status`: A dictionary that defines the bot's status. It can contain keys for playing,
  watching, listening, streaming, and custom, each with a list of possible statuses. It
  also contains an `every` key that defines the interval (in seconds) at which the status
  is updated. The `custom` type is sent as `discord.CustomActivity(name=...)`.

Here is an example of how to configure the Branding extension in your `config.yml` file:

```yaml
extensions:
  branding:
    enabled: true
    status:
      watching: ["you", "/help"] # you can also use streaming, playing, listening, and custom
      custom: ["Shipping features"]
      every: 300
```

## Important

Please note that the Branding extension will log a warning if `status` is not set up.

## Contributing

If you wish to contribute to the development of the Branding extension, please feel free
to submit a pull request. We appreciate your help in making this extension better.
