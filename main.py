import os
import re
import aiohttp
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Server ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is Running! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. Config ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"

# --- 3. Main Logic ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    
    # YouTube သို့မဟုတ် TikTok ဖြစ်ကြောင်း ပိုမိုကျယ်ပြန့်စွာ စစ်ဆေးခြင်း
    is_youtube = any(x in text.lower() for x in ["youtube.com", "youtu.be", "googleusercontent"])
    is_tiktok = "tiktok.com" in text.lower()

    if not is_youtube and not is_tiktok:
        return

    links = re.findall(r'(https?://[^\s]+)', text)
    if not links:
        return
        
    url = links[0]
    status_msg = await update.message.reply_text("ဗီဒီယို ရှာဖွေနေပါတယ်... ⏳")

    try:
        async with aiohttp.ClientSession() as session:
            # --- YouTube ---
            if is_youtube:
                # Cobalt API က လက်ရှိမှာ အကောင်းဆုံးမို့ သူ့ကိုပဲ အားကိုးပါမယ်
                payload = {"url": url, "videoQuality": "720"}
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                
                async with session.post("https://api.cobalt.tools/api/json", json=payload, headers=headers) as response:
                    res_json = await response.json()
                    
                    if res_json.get('status') in ['stream', 'redirect']:
                        v_url = res_json['url']
                        kb = [[InlineKeyboardButton("Download 📥", url=v_url)]]
                        
                        try:
                            await update.message.reply_video(video=v_url, caption="✅ YouTube Downloader", reply_markup=InlineKeyboardMarkup(kb))
                            await status_msg.delete()
                        except:
                            await status_msg.edit_text("⚠️ ဗီဒီယိုဖိုင် ကြီးနေသဖြင့် အောက်ကခလုတ်ဖြင့် ဒေါင်းပါ။", reply_markup=InlineKeyboardMarkup(kb))
                    else:
                        await status_msg.edit_text("❌ YouTube ဗီဒီယို ရှာမတွေ့ပါ။ Link ကို မူရင်းအတိုင်း ကူးထည့်ကြည့်ပါ။")

            # --- TikTok ---
            elif is_tiktok:
                async with session.get(f"https://www.tikwm.com/api/?url={url}") as response:
                    res_json = await response.json()
                    if res_json.get('code') == 0:
                        v_url = res_json['data']['play']
                        await update.message.reply_video(video=v_url, caption="✅ TikTok Done!")
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ TikTok ရှာမတွေ့ပါ။")

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("⚠️ API ခဏယိုးဒယားဖြစ်နေပါတယ်။ ခဏနေမှ ပြန်စမ်းပါ။")

# --- 4. Start ---
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is Started!")
    app.run_polling()
