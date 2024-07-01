# Top.gg Extension

The Top.gg extension is a powerful tool that allows your bot to interact with the Top.gg API. It requires a valid Top.gg token and is **disabled** by default.

## Features

The Top.gg extension performs the following tasks:

- It updates the server count of your bot on Top.gg every 30 minutes.
- It handles any exceptions that might occur during the update process and logs them.

## Usage

The Top.gg extension is a background task and does not provide any commands for interaction. Once enabled and properly configured, it will automatically perform its tasks without any further intervention.

## Configuration

The Top.gg extension requires the following configuration:

- `token`: Your Top.gg token. This is a string, and it is required for the extension to work.
- `enabled`: A boolean value that determines whether the extension is enabled or not. By default, this is set to `false`.

Here is an example of how to configure the Top.gg extension in your `config.yml` file:

```yaml
extensions:
  topgg:
    token: "your-topgg-token"
    enabled: true
```

Please replace `"your-topgg-token"` with your actual Top.gg token.

## Important

Please note that the Top.gg extension will not load if the `token` is not set up. The extension will log an error message and return.

## Contributing

If you wish to contribute to the development of the Top.gg extension, please feel free to submit a pull request. We appreciate your help in making this extension better.
