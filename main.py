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
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"

# --- 3. Main Logic ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    
    # YouTube သို့မဟုတ် TikTok ဖြစ်ကြောင်း စစ်ဆေးရန် (ပိုမိုကျယ်ပြန့်စွာ စစ်ဆေးမည်)
    is_youtube = any(x in text.lower() for x in ["youtube.com", "youtu.be", "googleusercontent.com/youtube"])
    is_tiktok = any(x in text.lower() for x in ["tiktok.com", "douyin.com"])

    if not is_youtube and not is_tiktok:
        return

    links = re.findall(r'(https?://[^\s]+)', text)
    if not links:
        return
        
    url = links[0]
    status_msg = await update.message.reply_text("ဗီဒီယို စစ်ဆေးနေပါတယ်... ⏳")

    join_button = InlineKeyboardButton("Join Channel 📢", url="https://t.me/kgamechannel")

    try:
        async with aiohttp.ClientSession() as session:
            
            # --- TIKTOK ---
            if is_tiktok:
                async with session.get(f"https://www.tikwm.com/api/?url={url}") as response:
                    res_json = await response.json()
                    if res_json.get('code') == 0:
                        video_url = res_json['data']['play']
                        kb = [[join_button]]
                        await update.message.reply_video(video=video_url, caption="✅ TikTok Done!", reply_markup=InlineKeyboardMarkup(kb))
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ TikTok ဗီဒီယို ရှာမတွေ့ပါ။")

            # --- YOUTUBE ---
            elif is_youtube:
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                # YouTube အတွက် Cobalt API ကို သုံးထားသည်
                payload = {"url": url, "videoQuality": "720"}
                
                async with session.post("https://api.cobalt.tools/api/json", json=payload, headers=headers) as response:
                    res_json = await response.json()
                    
                    if res_json.get('status') in ['stream', 'redirect']:
                        video_url = res_json['url']
                        kb = [[InlineKeyboardButton("Direct Download 📥", url=video_url)], [join_button]]
                        
                        try:
                            # 50MB အောက်ဆိုလျှင် တိုက်ရိုက်ပို့မည်
                            await update.message.reply_video(video=video_url, caption="✅ YouTube Done!", reply_markup=InlineKeyboardMarkup(kb))
                            await status_msg.delete()
                        except Exception:
                            # 50MB ကျော်လျှင် Link ပေးမည်
                            await status_msg.edit_text("⚠️ ဖိုင်ဆိုဒ်ကြီး၍ တိုက်ရိုက်ပို့မရပါ။ အောက်ကခလုတ်ဖြင့် ဒေါင်းပါ။", reply_markup=InlineKeyboardMarkup(kb))
                    else:
                        # အကယ်၍ Cobalt API က Error ပြခဲ့လျှင်
                        await status_msg.edit_text("❌ YouTube ဒေါင်းလုဒ်ဆွဲ၍ မရပါ။ Link မှန်မမှန် ပြန်စစ်ပါ။")

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("⚠️ API Error တက်သွားပါတယ်။ ခဏနေမှ ပြန်စမ်းပါ။")

# --- 4. Main Function ---
if __name__ == "__main__":
    t = Thread(target=run_web, daemon=True)
    t.start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is started!")
    app.run_polling()
