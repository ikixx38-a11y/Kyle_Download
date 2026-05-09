import os
import re
import aiohttp
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is Running! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. Configuration ---
# သတိပြုရန် - Token ကို Environment Variable ထဲမှာ သိမ်းဆည်းခြင်းက ပိုလုံခြုံပါတယ်
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"
TIKTOK_API = "https://www.tikwm.com/api/"
# YouTube အတွက် အခမဲ့ API တစ်ခု (Cobalt API စသည်ဖြင့် သုံးနိုင်သည်)
YOUTUBE_API = "https://cobalt.lucasvtiradentes.com/api/json" 

# --- 3. Logic Functions ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    links = re.findall(r'(https?://[^\s]+)', text)
    
    if not links:
        return
        
    url = links[0]
    status_msg = await update.message.reply_text("ဗီဒီယို စစ်ဆေးနေပါတယ်... ⏳")

    # Join Channel Button (Shared)
    keyboard = [[InlineKeyboardButton("Join Channel 📢", url="https://t.me/kgamechannel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        async with aiohttp.ClientSession() as session:
            # --- TikTok Case ---
            if "tiktok.com" in url:
                async with session.get(TIKTOK_API, params={'url': url}, timeout=30) as response:
                    res_json = await response.json()
                    if res_json.get('code') == 0:
                        video_url = res_json['data']['play']
                        await update.message.reply_video(video=video_url, caption="✅ TikTok Video ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ", reply_markup=reply_markup)
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ TikTok ဗီဒီယို ရှာမတွေ့ပါ။")

            # --- YouTube Case ---
            elif "youtube.com" in url or "youtu.be" in url:
                # API သုံးပြီး YouTube video link ယူခြင်း
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                payload = {"url": url, "vQuality": "720"}
                
                async with session.post("https://co.wuk.sh/api/json", json=payload, headers=headers) as response:
                    res_json = await response.json()
                    
                    if res_json.get('status') == 'stream' or res_json.get('status') == 'redirect':
                        video_url = res_json['url']
                        await update.message.reply_video(video=video_url, caption="✅ YouTube Video ဒေါင်းလုဒ်လုပ်ပြီးပါပြီ", reply_markup=reply_markup)
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ YouTube ဗီဒီယိုကို ဒေါင်းလုဒ်ဆွဲ၍မရပါ။ (မူပိုင်ခွင့် သို့မဟုတ် အရှည်ကြောင့် ဖြစ်နိုင်သည်)")
            
            else:
                await status_msg.edit_text("⚠️ TikTok သို့မဟုတ် YouTube link များသာ ပေးပို့ပေးပါ။")

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("⚠️ Error တစ်ခုခု တက်သွားပါတယ်။ ခဏနေမှ ပြန်စမ်းပါ။")

# --- 4. Main Function ---
if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    app = Application.builder().token(TOKEN).build()
    # MessageHandler ကို အသစ်ပြင်ထားတဲ့ handle_message ဆီ ချိတ်ပေးလိုက်ပါမယ်
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is successfully started!")
    app.run_polling()
