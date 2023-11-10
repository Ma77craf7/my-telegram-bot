import logging
import subprocess
import os
from configparser import ConfigParser
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext
import yt_dlp
from asyncio import ensure_future

# Load the token from the configuration file
config = ConfigParser()
config.read('config.ini')  # Make sure your configuration file is in the same directory as the script
telegram_token = config.get('Telegram', 'token')
image = config.get('Telegram', 'image')
site = config.get('Telegram', 'site')
botName = config.get('Telegram', 'name')

# Set up logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE,name=botName):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hey, I'm {name}, to see wonders use the /wonders command.")

# Handler for the /appunti command
async def appunti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=site)

# Handler for the /meraviglie command
async def meraviglie(update: Update, context: ContextTypes.DEFAULT_TYPE, image=image):
    chat_id = update.message.chat_id
    await context.bot.send_photo(chat_id, photo=open(image, "rb"))

# Handler for the /yt command to download YouTube videos
async def download_video(update: Update, context: CallbackContext) -> None:
    video_url = context.args[0] if context.args else None
    if not video_url:
        await update.message.reply_text('Please provide a valid YouTube video URL.')
        return

    try:
        chat_id = update.effective_chat.id
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        output_filename = f'video_{chat_id}.mp4'
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'outtmpl': output_filename,
            'progress_hooks': [lambda d: (ensure_future(download_progress_hook(d, update, context)))],
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        with open(output_filename, 'rb') as video_file:
            await context.bot.send_video(chat_id, video_file, caption='Video downloaded successfully!')

        os.remove(output_filename)

    except yt_dlp.DownloadError as e:
        await update.message.reply_text(f'Error downloading from YouTube: {str(e)}')
    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')

# Progress hook for video download
async def download_progress_hook(d: dict, update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if d['status'] == 'finished':
        await context.bot.send_message(chat_id, f'Download completed for a file!')

    elif d['status'] == 'error':
        await context.bot.send_message(chat_id, f'Error during download: {d["error"]}')

if __name__ == '__main__':
    # Build the application
    application = ApplicationBuilder().token(telegram_token).build()

    # Add handlers for commands
    # Start command handler
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Appunti command handler
    appunti_handler = CommandHandler('appunti', appunti)
    application.add_handler(appunti_handler)

    # Meraviglie command handler
    meravigle_handler = CommandHandler("meraviglie", meraviglie)
    application.add_handler(meravigle_handler)

    # YouTube downloader command handler
    yt_handler = CommandHandler('yt', download_video)
    application.add_handler(yt_handler)

    # Run the application with polling
    application.run_polling()
