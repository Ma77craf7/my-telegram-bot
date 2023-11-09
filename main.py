import logging
import subprocess
import os
from configparser import ConfigParser
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext
import yt_dlp
from asyncio import ensure_future
# Carica il token dal file di configurazione
config = ConfigParser()
config.read('config.ini')  # Assicurati che il tuo file di configurazione si trovi nella stessa directory dello script
telegram_token = config.get('Telegram', 'token')
image = config.get('Telegram', 'image')
site = config.get("Telegram", 'site')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
 )
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE,site):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey, sono Barbero, per vedere meravigle usa il commando /ceno")

async def appunti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=site)

async def meraviglie(update: Update, context: ContextTypes.DEFAULT_TYPE, image=image):
    chat_id = update.message.chat_id
    await context.bot.send_photo(chat_id, photo=open(image, "rb"))

async def download_video(update: Update, context: CallbackContext) -> None:
    video_url = context.args[0] if context.args else None
    if not video_url:
        await update.message.reply_text('Per favore, fornisci un URL valido di un video di YouTube.')
        return

    try:
        chat_id = update.effective_chat.id
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        output_filename = f'video_{chat_id}.mp4'
        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'outtmpl': output_filename,
            'progress_hooks': [lambda d: ensure_future(download_progress_hook(d, update, context))],
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        with open(output_filename, 'rb') as video_file:
            await context.bot.send_video(chat_id, video_file, caption='Video scaricato con successo!')

        os.remove(output_filename)

    except yt_dlp.DownloadError as e:
        await update.message.reply_text(f'Errore durante il download da YouTube: {str(e)}')
    except Exception as e:
        await update.message.reply_text(f'Si è verificato un errore: {str(e)}')

async def download_progress_hook(d: dict, update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if d['status'] == 'downloading':
        message = f'Scaricamento... {d["_percent_str"]} ETA: {d["_eta_str"]}'
        await context.bot.send_message(chat_id, message)
    elif d['status'] == 'finished':
        await context.bot.send_message(chat_id, 'Download completato!')
    elif d['status'] == 'error':
        await context.bot.send_message(chat_id, f'Errore durante il download: {d["error"]}')

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()

    # start handler
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # appunti link
    appunti_handler = CommandHandler('appunti', appunti)
    application.add_handler(appunti_handler)

    # meraviglie
    meravigle_handler = CommandHandler("meraviglie",meraviglie)
    application.add_handler(meravigle_handler)

    # youtube downloader
    yt_handler = CommandHandler('yt', download_video)
    application.add_handler(yt_handler)

    application.run_polling()