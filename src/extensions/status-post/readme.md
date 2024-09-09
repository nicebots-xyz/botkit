# Status Extension

The Status extension is a straightforward, yet essential part of your Botkit.
It requires minimal configuration and can be enabled or disabled as needed.

## Features

The Status extension periodically pushes the bot's status to a specified URL.
This can be useful for monitoring the bot's health and responsiveness.

## Usage

To use the Status extension, configure the `url` and `every` keys in the `config.yml` file or through environment variables. The bot will push its status to the specified URL at the configured interval.

## Configuration

The Status extension requires the following configuration:

- `enabled`: A boolean indicating whether the extension is enabled.
- `url`: The URL to which the bot's status will be pushed.
- `every`: The interval (in seconds) at which the bot's status will be pushed.

Example configuration in `config.yml`:

```yaml
status:
  enabled: true
  url: "http://example.com/status"
  every: 60
```

## Contributing
If you wish to contribute to the development of the Status extension, please feel free to submit a pull request. We appreciate your help in making this extension better.