# Ping Extension

The Ping extension is a straightforward, yet essential part of your Botkit.
It doesn't require any configuration and is **enabled** by default.

## Features

The Ping extension adds a `/ping` command to your bot.
When this command is invoked, the bot responds with a message indicating that it is online and operational.
This can be useful for quickly checking if your bot is responsive.
The Ping extension also serves an http endpoint at `/ping` that responds with a `200 OK` status code and the bot's name.

## Usage

To use the Ping extension type the `/ping` command. The bot should respond with a message, confirming its online status.
You can also send a `GET` request to the `/ping` endpoint to check if the bot is online.

```bash
curl http://localhost:5000/ping
```

## Configuration

The Ping extension does not require any configuration. It is enabled by default. If you wish to disable it, you can do so by setting its `enabled` key to `false` in the `config.yml` file or through environment variables.

## Contributing

If you wish to contribute to the development of the Ping extension, please feel free to submit a pull request. We appreciate your help in making this extension better.
