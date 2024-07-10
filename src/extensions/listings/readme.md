# Listings Extension

The Listings extension is a powerful tool that allows your bot to interact with various bot listing websites. It requires valid tokens for each listing website and is **disabled** by default.

## Features

The Listings extension performs the following tasks:

- It updates the server count of your bot on the listing websites every 30 minutes.
- It handles any exceptions that might occur during the update process and logs them.

## Usage

The Listings extension is a background task and does not provide any commands for interaction. Once enabled and properly configured, it will automatically perform its tasks without any further intervention.

## Configuration

The Listings extension requires the following configuration:

- `topgg_token`: Your Top.gg token. This is a string, and it is required for the Top.gg listing to work.
- `discordscom_token`: Your Discords.com token. This is a string, and it is required for the Discords.com listing to work.
- `enabled`: A boolean value that determines whether the extension is enabled or not. By default, this is set to `false`.

Here is an example of how to configure the Listings extension in your `config.yml` file:

```yaml
extensions:
  listings:
    topgg_token: "your-topgg-token"
    discordscom_token: "your-discordscom-token"
    enabled: true
```

Please replace `"your-topgg-token"` and `"your-discordscom-token"` with your actual tokens.

## Important

Please note that the Listings extension will not load if the `topgg_token` or `discordscom_token` is not set up. The extension will log an error message and return.

## Contributing

If you wish to contribute to the development of the Listings extension, please feel free to submit a pull request. We appreciate your help in making this extension better.