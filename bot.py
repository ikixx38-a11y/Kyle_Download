import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

# Bot Token ကို Render ရဲ့ Environment Variable မှာ BOT_TOKEN ဆိုပြီး ထည့်ပေးရပါမယ်
TOKEN = os.getenv('8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g')
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- TikTok Downloader Logic ---
def download_tiktok(url):
    # yt-dlp option များ (Watermark ကင်းစင်ပြီး အကောင်းဆုံး Quality ရရန်)
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        return 'video.mp4'

# --- Telegram Bot Commands ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 မင်္ဂလာပါ။ TikTok Link ပို့ပေးပါ။")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def handle_video(message):
    status_msg = bot.reply_to(message, "⏳ ဒေါင်းလုဒ်ဆွဲနေပါတယ်...")
    try:
        video_file = download_tiktok(message.text)
        with open(video_file, 'rb') as v:
            bot.send_video(message.chat.id, v)
        os.remove(video_file) # နေရာလွတ်စေရန် ပြန်ဖျက်ခြင်း
        bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ အမှားအယွင်းရှိပါသည်- {str(e)}", message.chat.id, status_msg.message_id)

# --- Render Web Server (Keep Alive) ---
@server.route("/")
def webhook():
    return "Bot is alive!", 200

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Bot ကို Thread တစ်ခုဖြင့် Run ရန်
    Thread(target=run_bot).start()
    # Render အတွက် Port ဖွင့်ပေးခြင်း
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)
