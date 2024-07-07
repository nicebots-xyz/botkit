# Nice-Errors Extension

The Nice-Errors extension is an essential tool for your Botkit, designed to enhance error handling by providing user-friendly error messages during command execution. This feature improves the user experience by ensuring that errors are communicated effectively and clearly.

## Features

The Nice-Errors extension intercepts errors that occur during the execution of application commands. Instead of displaying raw error messages, it formats them into more understandable text and provides guidance or feedback to the user. This can significantly improve the interaction between the bot and its users by making error messages less intimidating and more informative.

## Usage

When a command execution leads to an error, the Nice-Errors extension automatically catches this error. It then checks the type of error and responds with a customized, user-friendly message. This process is entirely automated, requiring no manual intervention from the user or developer.

## Configuration

The Nice-Errors extension can be enabled or disabled as needed. By default, it is enabled to ensure that your bot always provides helpful feedback to users during errors. Here's how you can configure it:

- `enabled`: A boolean value that determines whether the Nice-Errors feature is active. Set to `True` by default.

To adjust this setting, you can modify the `config.yml` file or use environment variables. For example:

```yaml
nice_errors:
  enabled: True
```

## Contributing

Contributions to the Nice-Errors extension are highly encouraged. If you have suggestions for improving the error messages or adding support for more types of errors, please submit a pull request. Your input is invaluable in making this extension more effective for all users.
