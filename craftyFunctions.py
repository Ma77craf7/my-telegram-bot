# Importing necessary libraries
import sqlite3 as sq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ContextTypes, CommandHandler, CallbackContext
import logging
from configparser import ConfigParser
from crafty_client import Crafty4

# Reading configuration from the config file
config = ConfigParser()
config.read('config.ini')  # Make sure your configuration file is in the same directory as the script
default_token = config.get('Crafty', 'default_token')
crafty_url = config.get('Crafty', 'url')

# Set up logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Function to initialize the database
async def init_db():
    conn = sq.connect('crafty_tokens.db')
    cursor = conn.cursor()

    # Creating the table for chat information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_info (
            chat_id INTEGER PRIMARY KEY,
            crafty_token TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Function to save the Crafty token for a specific chat
async def save_crafty_token(chat_id, crafty_token):
    conn = sq.connect('crafty_tokens.db')
    cursor = conn.cursor()

    # Inserting or updating the token for the specified chat
    cursor.execute('''
        INSERT OR REPLACE INTO chat_info (chat_id, crafty_token)
        VALUES (?, ?)
    ''', (chat_id, crafty_token))

    conn.commit()
    conn.close()

# Function to get the Crafty token for a specific chat
async def get_crafty_token(chat_id):
    conn = sq.connect('crafty_tokens.db')
    cursor = conn.cursor()

    # Retrieving the token for the specified chat
    cursor.execute('''
        SELECT crafty_token FROM chat_info WHERE chat_id=?
    ''', (chat_id,))
    
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None

# Function to update the Crafty token for a specific chat
async def new_token(update: Update, context: CallbackContext):
    await init_db()
    new_crafty_token=context.args[0] if context.args else None
    chat_id = update.effective_chat.id
    if new_crafty_token:
        await save_crafty_token(chat_id, new_crafty_token)
        message = f"Crafty token aggiornato per la chat"
    else:
        message = "Per favore, fornisci un nuovo token di Crafty."
    await context.bot.send_message(chat_id, message)

# Function to get the ID of the currently running server
async def get_running_server_id(c):
    servers = c.list_mc_servers()
    for i in servers:
        g = c.get_server_stats(i["server_id"])
        if g["running"]:
            return i["server_id"]

# Function to check and display the status of the server
async def server_status(update: Update, context: ContextTypes.DEFAULT_TYPE, crafty_url=crafty_url):
    chat_id = update.effective_chat.id
    try:
        token = await get_crafty_token(chat_id)
    except:
        global default_token
        token = default_token
    c = Crafty4(crafty_url, token, verify_ssl=True)
    server_id = await get_running_server_id(c)
    g = c.get_server_stats(server_id)
    message = f"status of server {g['server_id']['server_name']}\n\tonline: {g['running']}\n\tonline players: {g['online']}"
    if g['online']:
        keyboard = [[InlineKeyboardButton("see players", callback_data=f'seeplayers_{g["players"]}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        reply_markup = None
    await context.bot.send_message(chat_id, message, reply_markup=reply_markup)

# Callback function to display online players when "see players" button is pressed
async def see_players_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    try:
        players = eval(query.data.split('_')[1])
        message = ""
        for player in players:
            message += f"{player}\n"
        await context.bot.send_message(chat_id, message)
    except Exception as e:
        print(f"An error occurred in see_players_callback: {e}")
        await context.bot.send_message(chat_id, f"An error occurred while processing your request.\n{e}")
    await query.answer(text=None, show_alert=False)

# Try to create the database file and initialize the database; log any exceptions
try:
    with open("crafty_tokens.db", 'x') as f:
        pass
except Exception as e:
    logging.exception(e)
    pass