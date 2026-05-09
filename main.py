import os
import re
import aiohttp
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (Render မှာ အိပ်မပျော်အောင်) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is Online! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. Configuration ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"

# --- 3. Logic Functions ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    
    # YouTube သို့မဟုတ် TikTok Link ဟုတ်မဟုတ် စစ်ဆေးခြင်း
    # သင်ပြသော googleusercontent.com/youtube format ကိုပါ ထည့်သွင်းထားသည်
    is_youtube = any(x in text.lower() for x in ["youtube.com", "youtu.be", "googleusercontent.com/youtube"])
    is_tiktok = any(x in text.lower() for x in ["tiktok.com", "douyin.com"])

    if not is_youtube and not is_tiktok:
        return

    # Link ကို ရှာထုတ်ခြင်း
    links = re.findall(r'(https?://[^\s]+)', text)
    if not links:
        return
        
    url = links[0]
    status_msg = await update.message.reply_text("ဗီဒီယို စစ်ဆေးနေပါတယ်... ⏳")

    # Join Channel Button
    kb_join = [[InlineKeyboardButton("Join Channel 📢", url="https://t.me/kgamechannel")]]

    try:
        async with aiohttp.ClientSession() as session:
            # --- YOUTUBE CASE ---
            if is_youtube:
                # Cobalt API သုံးပြီး ဒေါင်းလုဒ် Link ယူခြင်း
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                payload = {"url": url, "videoQuality": "720"}
                
                async with session.post("https://api.cobalt.tools/api/json", json=payload, headers=headers) as response:
                    res_json = await response.json()
                    
                    if res_json.get('status') in ['stream', 'redirect']:
                        video_url = res_json['url']
                        
                        # Download Button for user
                        kb = [
                            [InlineKeyboardButton("Direct Download 📥", url=video_url)],
                            [InlineKeyboardButton("Join Channel 📢", url="https://t.me/kgamechannel")]
                        ]
                        
                        try:
                            # 50MB ထက်နည်းရင် Telegram ထဲ တန်းပို့မယ်
                            await update.message.reply_video(
                                video=video_url, 
                                caption="✅ YouTube ဗီဒီယို ရပါပြီ။\n(ဖိုင်ကြီး၍ မပွင့်ပါက Direct Download ကိုနှိပ်ပါ)",
                                reply_markup=InlineKeyboardMarkup(kb)
                            )
                            await status_msg.delete()
                        except Exception:
                            # 50MB ထက်ကျော်ရင် Link ပဲပေးမယ်
                            await status_msg.edit_text(
                                "⚠️ ဗီဒီယိုဖိုင် အရမ်းကြီးနေသဖြင့် တိုက်ရိုက်ပို့၍ မရပါ။\nအောက်က Button ကိုနှိပ်ပြီး ဒေါင်းလုဒ်ဆွဲပါခင်ဗျာ။",
                                reply_markup=InlineKeyboardMarkup(kb)
                            )
                    else:
                        await status_msg.edit_text("❌ YouTube ဗီဒီယို ရှာမတွေ့ပါ။ Link ကို ပြန်စစ်ပေးပါ။")

            # --- TIKTOK CASE ---
            elif is_tiktok:
                async with session.get(f"https://www.tikwm.com/api/?url={url}") as response:
                    res_json = await response.json()
                    if res_json.get('code') == 0:
                        video_url = res_json['data']['play']
                        await update.message.reply_video(
                            video=video_url, 
                            caption="✅ TikTok Done!",
                            reply_markup=InlineKeyboardMarkup(kb_join)
                        )
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ TikTok ဗီဒီယို ရှာမတွေ့ပါ။")

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("⚠️ API Error တက်သွားပါတယ်။ ခဏနေမှ ပြန်စမ်းပါ။")

# --- 4. Main Function ---
if __name__ == "__main__":
    # Web server thread start
    t = Thread(target=run_web, daemon=True)
    t.start()
    
    # Bot start
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is successfully running! 🚀")
    app.run_polling()
