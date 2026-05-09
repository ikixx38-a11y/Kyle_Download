import os
import re
import aiohttp
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (For Render 24/7) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is Online! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. Configuration ---
# သင့်ရဲ့ Bot Token ကို ဒီမှာထည့်ပါ
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"

# --- 3. Main Logic ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    links = re.findall(r'(https?://[^\s]+)', text)
    
    if not links:
        return
        
    url = links[0]
    status_msg = await update.message.reply_text("ဗီဒီယို စစ်ဆေးနေပါတယ်... ⏳")

    # Common Keyboard (Join Channel)
    join_button = InlineKeyboardButton("Join Channel 📢", url="https://t.me/kgamechannel")

    try:
        async with aiohttp.ClientSession() as session:
            
            # --- CASE
