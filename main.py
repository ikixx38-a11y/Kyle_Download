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
    return "Bot is Running! 🚀"

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
        # Link ရှာထုတ်ခြင်း
        links = re.findall(r'(https?://[^\s]+)', text)
        if not links:
            return
            
        tiktok_url = links[0]
        status_msg = await update.message.reply_text("ဗီဒီယို ရှာနေပါတယ်... ⏳")

        try:
            # API ဆီကနေ Video data တောင်းမယ်
            async with aiohttp.ClientSession() as session:
                async with session.get(TIKTOK_API, params={'url': tiktok_url}, timeout=30) as response:
                    res_json = await response.json()
                    
                    if res_json.get('code') == 0:
                        video_url = res_json['data']['play']
                        
                        # Join Channel ခလုတ်ဖန်တီးမယ်
                        keyboard = [
                            [InlineKeyboardButton("Join Channel 📢", url="https://t.me/kgamechannel")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        # ဗီဒီယိုပို့မယ်
                        await update.message.reply_video(
                            video=video_url, 
                            caption="✅ Watermark မပါဘဲ ဒေါင်းလုဒ်ဆွဲပြီးပါပြီ။\n\nChannel: @kgamechannel",
                            reply_markup=reply_markup
                        )
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ ဗီဒီယို ရှာမတွေ့ပါ။ Link မှန်ရဲ့လား ပြန်စစ်ပေးပါ။")
        except Exception as e:
            print(f"Error: {e}")
            await status_msg.edit_text("⚠️ API Error တက်သွားပါတယ်။ ခဏနေမှ ပြန်စမ်းပါ။")

# --- 4. Main ---
def main():
    # Web server ကို background thread နဲ့ အရင်စမယ်
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Telegram Bot စတင်မယ်
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    
    print("TikTok Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
