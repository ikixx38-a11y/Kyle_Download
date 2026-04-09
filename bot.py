import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

# --- ဒီနေရာမှာ သင့် Token ကို အတိအကျ ထည့်ပါ ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g" 
# ဥပမာ - TOKEN = "12345678:AAFdscs..."

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

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
def welcome(message):
    bot.reply_to(message, "TikTok link ပို့ပေးပါ၊ ဒေါင်းပေးပါ့မယ်။")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text or "douyin.com" in m.text)
def handle_tiktok(message):
    wait = bot.reply_to(message, "⏳ ခဏစောင့်ပါ...")
    try:
        file = download_tiktok(message.text)
        with open(file, 'rb') as v:
            bot.send_video(message.chat.id, v)
        if os.path.exists(file):
            os.remove(file)
        bot.delete_message(message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, wait.message_id)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Bot ကို Thread နှင့် Run ခြင်း
    Thread(target=run_bot).start()
    # Render အတွက် Port ချိတ်ခြင်း
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
