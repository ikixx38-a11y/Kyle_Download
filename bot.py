import os
import telebot
import yt_dlp
from fastapi import FastAPI
import uvicorn
from threading import Thread

# Bot API Token
TOKEN = os.getenv('8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g')
bot = telebot.TeleBot(TOKEN)
app = FastAPI()

# Render အတွက် Web Endpoint
@app.get("/")
def index():
    return {"status": "Bot is running"}

def download_tiktok(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        return 'video.mp4'

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "TikTok link ပို့ပေးပါ၊ Watermark မပါဘဲ ဒေါင်းပေးမယ်။")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def handle_msg(message):
    temp_msg = bot.reply_to(message, "⏳ ခဏစောင့်ပါ...")
    try:
        file_path = download_tiktok(message.text)
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove(file_path)
        bot.delete_message(message.chat.id, temp_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, temp_msg.message_id)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Bot ကို Thread တစ်ခုနဲ့ Run မယ်
    Thread(target=run_bot).start()
    # Web Server ကို Render Port မှာ Run မယ်
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
