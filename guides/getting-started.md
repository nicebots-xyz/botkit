# Getting Started with Botkit and Pycord: Creating Your First Bot Extension

This comprehensive tutorial will guide you through the process of setting up Botkit, creating your first bot extension using Pycord, and understanding the core concepts of Discord bot development.

## Prerequisites

Before we begin, ensure you have the following:

1. Python 3.11 or higher installed
2. Basic understanding of Python and Discord concepts
3. A Discord account and access to the Discord Developer Portal

> [!IMPORTANT]
> If you haven't already, create a Discord application and bot user in the [Discord Developer Portal](https://discord.com/developers/applications). You'll need the bot token for later steps.

## Step 1: Install Git

If you don't have Git installed, you'll need to install it to clone the Botkit repository.

1. Visit the [Git website](https://git-scm.com/downloads) and download the appropriate version for your operating system.
2. Follow the installation instructions for your OS.

> [!TIP]
> On Windows, you can use the Git Bash terminal that comes with Git for a Unix-like command-line experience.

To verify Git is installed correctly, open a terminal or command prompt and run:

```bash
git --version
```

You should see the installed Git version in the output.

## Step 2: Clone the Botkit Repository

Now that Git is installed, let's clone the Botkit repository:

1. Open a terminal or command prompt.
2. Navigate to the directory where you want to store your bot project.
3. Run the following command:

```bash
git clone https://github.com/nicebots-xyz/botkit
```

4. Once the cloning is complete, navigate into the Botkit directory:

```bash
cd botkit
```

> [!NOTE]
> Cloning the repository creates a local copy of Botkit on your machine, allowing you to build your bot using the Botkit framework.

## Step 3: Set Up a Virtual Environment (Optional but Recommended)

It's a good practice to use a virtual environment for your Python projects. This keeps your project dependencies isolated from your system-wide Python installation.

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:
    - On Windows:
      ```
      venv\Scripts\activate
      ```
    - On macOS and Linux:
      ```
      source venv/bin/activate
      ```

> [!TIP]
> You'll know the virtual environment is active when you see `(venv)` at the beginning of your terminal prompt.

## Step 4: Install Dependencies

Install the required dependencies using PDM (Python Dependency Manager):

1. If you haven't installed PDM yet, install it using pip:

```bash
pip install pdm
```

2. Install the project dependencies:

```bash
pdm install
```

> [!NOTE]
> PDM will read the `pyproject.toml` file and install all necessary dependencies for Botkit.

## Step 5: Configure Your Bot

1. In the root directory of your Botkit project, create a file named `config.yml`.
2. Open `config.yml` in a text editor and add the following content:

```yaml
bot:
  token: "YOUR_BOT_TOKEN_HERE"
```

Replace `YOUR_BOT_TOKEN_HERE` with the actual token of your Discord bot.

> [!CAUTION]
> Never share your bot token publicly or commit it to version control. Treat it like a password.

## Step 6: Create a New Extension Folder

Now, let's create a new folder for our extension:

1. Navigate to the `src/extensions` directory in your Botkit project.
2. Create a new folder called `my_first_extension`:

```bash
mkdir src/extensions/my_first_extension
```

## Step 7: Create the `__init__.py` File

The `__init__.py` file is crucial for Python to recognize the directory as a package:

1. Inside the `my_first_extension` folder, create a file named `__init__.py`:

```bash
touch src/extensions/my_first_extension/__init__.py
```

2. Open `__init__.py` in your preferred text editor and add the following content:

```python
from .main import setup, default, schema

__all__ = ["setup", "default", "schema"]
```

> [!NOTE]
> This file imports and exposes the necessary components from our `main.py` file (which we'll create next). It allows Botkit to access these components when loading the extension.

## Step 8: Create the `main.py` File

The `main.py` file will contain the main logic for our extension:

1. In the `my_first_extension` folder, create a file named `main.py`:

```bash
touch src/extensions/my_first_extension/main.py
```

2. Open `main.py` in your text editor and add the following content:

```python
import discord
from discord.ext import commands
from typing import Dict, Any

class MyFirstExtension(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

def setup(bot: discord.Bot):
    bot.add_cog(MyFirstExtension(bot))

default = {
    "enabled": True
}

schema = {
    "enabled": bool
}
```

Let's break down what we've done here:

- We import the necessary modules from discord and discord.ext.
- We use `typing` to add type hints, which improves code readability and helps catch errors early.
- We define a `MyFirstExtension` class that inherits from `commands.Cog`. This class will contain our commands and listeners.
- The `setup` function is required by Botkit to add our cog to the bot.
- We define `default` and `schema` dictionaries for the extension's configuration.

> [!TIP]
> Using type hints (like `bot: discord.Bot`) helps catch errors early and improves code readability. It's a good practice to use them consistently in your code.

## Step 9: Adding Commands

Now, let's add some commands to our extension. We'll create a simple "hello" command and a more complex "userinfo" command.

Add the following methods to your `MyFirstExtension` class in `main.py`:

```python
@discord.slash_command(name="hello", description="Say hello to the bot")
async def hello(self, ctx: discord.ApplicationContext):
    await ctx.respond(f"Hello, {ctx.author.name}!")

@discord.slash_command(name="userinfo", description="Get information about a user")
async def userinfo(
    self,
    ctx: discord.ApplicationContext,
    user: discord.Option(discord.Member, "The user to get info about", default=None)
):
    user = user or ctx.author
    embed = discord.Embed(title=f"User Info - {user.name}", color=user.color)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles[1:]]) or "None")
    await ctx.respond(embed=embed)
```

Let's explain these commands:

1. The `hello` command:
    - Uses the `@discord.slash_command` decorator to create a slash command.
    - Takes only the `ctx` (context) parameter, which is automatically provided by Discord.
    - Responds with a greeting using the author's name.

2. The `userinfo` command:
    - Also uses `@discord.slash_command` to create a slash command.
    - Takes an optional `user` parameter, which defaults to the command author if not provided.
    - Creates an embed with various pieces of information about the user.
    - Responds with the created embed.

> [!NOTE]
> Slash commands are the modern way to create Discord bot commands. They provide better user experience and are easier to discover than traditional prefix-based commands.

## Step 10: Adding an Event Listener

Let's add an event listener to our extension to demonstrate how to respond to Discord events. We'll add a simple listener that logs when the bot is ready.

Add the following method to your `MyFirstExtension` class in `main.py`:

```python
@commands.Cog.listener()
async def on_ready(self):
    print(f"Bot is ready! Logged in as {self.bot.user}")
```

This listener will print a message to the console when the bot has successfully connected to Discord.

> [!TIP]
> Event listeners are great for performing actions based on Discord events, such as when a member joins a server or when a message is deleted.

## Step 11: Final `main.py` File

Your complete `main.py` file should now look like this:

```python
import discord
from discord.ext import commands
from typing import Dict, Any

class MyFirstExtension(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="hello", description="Say hello to the bot")
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Hello, {ctx.author.name}!")

    @discord.slash_command(name="userinfo", description="Get information about a user")
    async def userinfo(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(discord.Member, "The user to get info about", default=None)
    ):
        user = user or ctx.author
        embed = discord.Embed(title=f"User Info - {user.name}", color=user.color)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles[1:]]) or "None")
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot is ready! Logged in as {self.bot.user}")

def setup(bot: discord.Bot):
    bot.add_cog(MyFirstExtension(bot))

default = {
    "enabled": True
}

schema = {
    "enabled": bool
}
```

## Step 12: Running Your Bot

Now that we've created our extension, let's run the bot:

1. Make sure you're in the root directory of your Botkit project.
2. Run the following command:

```bash
pdm run start
```

> [!IMPORTANT]
> Ensure your bot token is correctly set in the `config.yml` file before running the bot.

If everything is set up correctly, you should see the "Bot is ready!" message in your console, indicating that your bot is now online and ready to respond to commands.

## Conclusion

Congratulations! You've now created your first bot extension using Botkit and Pycord. This extension includes:

1. A simple "hello" slash command
2. A more complex "userinfo" slash command that creates an embed
3. An event listener for the "on_ready" event

> [!TIP]
> To continue improving your bot, consider adding more commands, implementing additional event listeners, or integrating with external APIs or databases.

> [!WARNING]
> Always be cautious when handling user data and permissions in your bot. Ensure you're following Discord's Terms of Service and Developer Policy.

Remember to always use type hinting in your code. It helps with code readability, catches potential errors early, and provides better autocomplete suggestions in many IDEs.

Happy coding, and enjoy building your Discord bot!