# Branding Extension

The Branding extension is a versatile tool that allows you to customize your bot's presence and embeds. It is **enabled** by default.

## Features

The Branding extension performs the following tasks:

- It updates the bot's status every 5 minutes by default. The status can be set to playing, watching, listening, or streaming.
- It allows customization of the embed's footer, color, and author.

## Usage

The Branding extension is a background task and does not provide any commands for interaction. Once properly configured, it will automatically perform its tasks without any further intervention.

## Configuration

The Branding extension requires the following configuration:

- `status`: A dictionary that defines the bot's status. It can contain keys for playing, watching, listening, and streaming, each with a list of possible statuses. It also contains an `every` key that defines the interval (in seconds) at which the status is updated.
- `embed`: A dictionary that defines the embed's footer, color, and author. The footer can contain a value (a string or a list of strings), a boolean for whether to include the time, a timezone, and a separator.

Here is an example of how to configure the Branding extension in your `config.yml` file:

```yaml
extensions:
  branding:
    enabled: true
    status:
      watching: ["you", "/help"]  # in conjunction, you can also use streaming, playing, and listening
      every: 300
    embed:
      footer:
        value: ["footer"]
        time: true
        tz: "UTC"
        separator: "|"
      color: 0x00FF00
      author: "Nice Bot"
      author_url: "https://picsum.photos/512"
```

## Important

Please note that the Branding extension will not load if both the `status` or `embed` configurations are not set up. The extension will log an error message and return.

## Contributing

If you wish to contribute to the development of the Branding extension, please feel free to submit a pull request. We appreciate your help in making this extension better.
