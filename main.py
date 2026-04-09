import os
import re
import aiohttp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (Render အတွက်) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "TikTok Bot is Online! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. Configuration ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"
TIKTOK_API = "https://www.tikwm.com/api/"

# --- 3. TikTok Logic ---
async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    if "tiktok.com" in text:
        links = re.findall(r'(https?://[^\s]+)', text)
        if not links: return
            
        tiktok_url = links[0]
        status_msg = await update.message.reply_text("ဗီဒီယို ရှာနေပါတယ်... ⏳")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(TIKTOK_API, params={'url': tiktok_url}) as response:
                    res_json = await response.json()
                    if res_json.get('code') == 0:
                        video_url = res_json['data']['play']
                        await update.message.reply_video(video=video_url, caption="✅ Success!")
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ ရှာမတွေ့ပါ။")
        except:
            await status_msg.edit_text("⚠️ Error!")

# --- 4. Main ---
if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    app.run_polling()
