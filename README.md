# Mailgram - Forward your emails to Telegram

Mailgram is a simple Python script that forwards your emails to Telegram. It is designed to be used with a cron job, so that you can receive your emails on Telegram.

## Installation

`pip install imapclient`

## Configuration

You need to create a `config.json` file in the same directory as the script. The file should look like this:

```
{
    "proxies": {      // Optional
        "http": "http://127.0.0.1:7890",
        "https": "https://127.0.0.1:7890"
    },
    "interval": 60,   // Fetch Interval in seconds
    "token": "your-bot-token",
    "chatid": 114514, // Your chat id
    "mails": [
        {
            "protocol": "imap", // Currently only IMAP is supported
            "address": "imap.example.com",
            "user": "example@example.com",
            "password": "password"
        }
    ]
}
```
