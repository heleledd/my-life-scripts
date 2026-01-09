# test things out with telegram API

from turtle import update
from typing import Final
from os import getenv
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN: Final = getenv('bot_token')
BOT_USERNAME: Final = "@budget_brain_25_bot"

# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi Heledd! You started me up!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Help!')

# responses
async def handle_response(text: str) -> str:
    # you could add an AI into here!
    # Define a simple response logic
    text = text.lower()
    if 'hello' in text:
        return 'Hello! How can I assist you today?'
    elif 'help' in text:
        return 'Sure! You can ask me about your bank statements or any other queries.'
    else:
        return "I'm not sure how to respond to that. Try asking for help!"
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = str(update.message.text).lower()
    
    logging.info(f'User {update.message.from_user.first_name} in {message_type} sent a message: {text}')
    response = await handle_response(text)
    await update.message.reply_text(response)