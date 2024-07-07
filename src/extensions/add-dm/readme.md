# Add-DM Extension

The Add-DM extension is a valuable addition to your Botkit, designed to automatically send a direct message (DM) to the user who adds the bot to a guild. This feature enhances user engagement by providing immediate acknowledgment and guidance upon installation.

## Features

The Add-DM extension automatically triggers a DM to the user who adds the bot to a server. This message can be customized to include instructions, a welcome message, or any other information deemed necessary by the bot owner. It's an excellent way for bot developers to start engaging with new users right away.

## Usage

Upon the bot being added to a guild, it checks for the necessary permissions and identifies the user who added the bot. It then sends a predefined message to this user. The message can be customized in the bot's configuration file.

## Configuration

The Add-DM extension requires minimal configuration, allowing for the customization of the message sent to the user. Here's a basic outline of the configurable options:

- `enabled`: Determines whether the Add-DM feature is active. Set to `True` by default.
- `message`: The message template sent to the user. Supports placeholders for dynamic content such as `{user.mention}` to mention the user.

To customize the message, edit the `config.yml` file or set the appropriate environment variables. For example:

```yaml
add_dm:
  enabled: True
  message: "Hello, {user.mention}! Thank you for adding me to your server. Type `/help` to see what I can do!"
```

## Contributing

Contributions to the Add-DM extension are welcome. If you have ideas on how to improve this extension or want to add new features, please submit a pull request. Your contributions are valuable in making this extension more useful for everyone.
