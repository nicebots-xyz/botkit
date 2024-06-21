# Botkit: A Framework for Building Discord Bots with py-cord

## What is Botkit?

Botkit is a framework for building Discord bots. It is designed to simplify the process of creating and managing Discord bots by providing a modular architecture and a set of tools and utilities.

## What Botkit is NOT

Botkit is not a pre-built Discord bot. Instead, it is a starting point for building your own custom Discord bot. You are expected to edit and modify the provided code to suit your specific requirements.

## Features

- **Modular Design**: The bot is designed with a modular architecture, allowing you to easily enable or disable specific extensions or features.
- **Extensible**: The bot supports two types of extensions:
  - **Default Extensions**: These are built-in extensions located in the `src/extensions` directory, such as the `ping` extension for a simple ping command.
  - **Installable Python Modules**: You can install and use external Python modules as extensions for the bot.
- **Configurable**: The bot's configuration, including enabled extensions and bot token, is managed through a `config.yml` file.
- **Easy Setup**: Botkit simplifies the setup process by providing a well-structured project template and configuration management.

## Requirements

- [pdm](https://pdm-project.org/en/latest/) - A modern Python packaging and dependency management tool.
- Python 3.11
- A Discord bot token. You can create a new bot and obtain a token from the [Discord Developer Portal](https://discord.com/developers/applications).

## Installation

1. Clone the repository and navigate to the project directory.
2. Install the required dependencies using `pdm`:

```
pdm install
```

## Setup

### Yaml Configuration
You can set up the `config.yml` file with your bot token and desired extensions. Here's an example configuration:

```yaml
extensions:
  topgg:
    enabled: false
    token: "your_top.gg_token"
  ping:
    enabled: true
bot:
  token: "your_bot_token"
logging:
  level: INFO
```

### Environment Variables
Alternatively, you can set the bot token and other configuration options using environment variables. You can set any variable as you would in the `config.yml` file, but with the `BOTKIT__` prefix, and `__` to separate nested keys. To set lists, use regular json syntax.
```env
BOTKIT__bot__token=your_bot_token
BOTKIT__extensions__topgg__enabled=false
BOTKIT__extensions__ping__enabled=true
BOTKIT__logging__level=INFO
```

## Default Extensions

### Ping Extension

The `ping` extension adds a slash command (`/ping`) to the bot. When a user types `/ping`, the bot will respond with `Pong!`. This extension demonstrates how to set up and register slash commands with py-cord.
The `/ping` command has two options:
- `ephemeral`: Whether the response should be ephemeral (visible only to the user who invoked the command). Default is `false`.
- `embed`: Whether the response should be an embed. Default is `false`.

### Top.gg Extension

The `topgg` extension is designed for bots listed on [top.gg](https://top.gg). When enabled, it automatically posts the bot's server count, shard count, and other stats to the top.gg API.

### Branding Extension

The `branding` extension allows you to customize the bot's online presence, as well as the default embed color, footer and author throughout the entire bot.
## Adding Extensions

### Built-in Extensions

Built-in extensions are located in the `src/extensions` directory. To enable a built-in extension, set `enabled: true` in the corresponding section of the `config.yml` file. By default, priority is given to built-in extensions over external Python modules.

### Python Module Extensions

To add a Python module as an extension, install it using pdm (`pdm add <module_name>`), and then set it up in the `config.yml` file under the `extensions` section.

Each extension must export a `setup` function with the following signature:

```python
def setup(bot: discord.Bot, logger: logging.Logger, config: dict):
    # Extension setup code here
```

- `bot`: The Discord bot instance.
- `logger`: A logger instance for logging messages.
- `config`: The configuration dictionary for the extension from the `config.yml` file. All config keys will always be lowercased for compatibility with environment variables.

## Contributing

We welcome contributions to this project! Please follow the [gitmoji.dev](https://gitmoji.dev) convention for commit messages and submit pull requests with descriptive commit messages.

## Built With

- [py-cord](https://github.com/Pycord-Development/pycord)
- [pdm](https://pdm-project.org/en/latest/)

## Code Style and Linting

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. We recommend using a linter like [black](https://github.com/psf/black) to ensure your code adheres to the style guidelines.
We provide a command to lint the code using `pdm run lint`. For this to work you have to install the development dependencies using `pdm install -d` if you haven't already.

## Deployment

Botkit is designed to be deployed on various platforms, including cloud services like [Heroku](https://www.heroku.com/) or [DigitalOcean](https://www.digitalocean.com/). Refer to the documentation of your preferred hosting platform for deployment instructions.
A `Dockerfile` is included in the project for containerized deployments, as well as a GitHub action including tests and linting.
You can export the requirements to a `requirements.txt` file using `pdm run export`, run the tests using `pdm run tests` and lint the code using `pdm run lint`.
In order for the GitHub tests to pass, you need to make sure you linted your code, that the tests pass and that you exported the requirements if you made changes to the dependencies.

## Support and Resources

If you encounter any issues or have questions about Botkit, feel free to open an issue on the [GitHub repository](https://github.com/nicebots-xyz/botkit). You can also join the [official Discord server](https://paill.at/OjTuQ) for support and discussions.

## License

This project is licensed under the [MIT License](LICENSE).
