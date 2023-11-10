# My  Telegram Bot

This is a simple Telegram bot written in Python that provides various functionalities, including viewing notes, sharing interesting content, and downloading YouTube videos. The bot is built using the Telegram Bot API and relies on the `yt_dlp` library for YouTube video downloading.

## Features

1. **Start Command**
   - `/start`: Initiates a conversation with the bot and provides a welcome message.

2. **Appunti Command**
   - `/appunti`: Shares notes or links to resources. The content is loaded from a configuration file.

3. **Meraviglie Command**
   - `/meraviglie`: Shares an image with the user. The image path is specified in the configuration file.

4. **YouTube Downloader**
   - `/yt <video_url>`: Downloads YouTube videos. The downloaded video is sent to the user, and progress messages are provided during the download. **Note: Requires ffmpeg to be installed on your system.**

## Prerequisites

Before running the bot, make sure to create a `config.ini` file in the same directory as the script, containing the following information:

```ini
[Telegram]
token = YOUR_TELEGRAM_BOT_TOKEN
image = PATH_TO_IMAGE_FILE
site = LINK_TO_SITE_OR_NOTES
name = NAME_OF_THE_BOT
