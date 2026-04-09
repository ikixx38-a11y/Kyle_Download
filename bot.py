import os
import telebot
import yt_dlp
from flask import Flask, request

# Bot Setting
TOKEN = os.getenv('8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g')
# Render က ပေးတဲ့ URL (ဥပမာ- https://your-app.onrender.com)
URL = os.getenv('RENDER_EXTERNAL_URL') 
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# TikTok Downloader Function
def download_tiktok(video_url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        return 'video.mp4'

# Webhook Route
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + '/' + TOKEN)
    return "Bot is alive and Webhook is set!", 200

# Bot Commands
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "TikTok Link ပို့ပေးပါ၊ ဒေါင်းပေးပါမယ်။")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def handle_tiktok(message):
    msg = bot.reply_to(message, "⏳ ခဏစောင့်ပါ...")
    try:
        file = download_tiktok(message.text)
        with open(file, 'rb') as v:
            bot.send_video(message.chat.id, v)
        os.remove(file)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: ဒေါင်းမရပါ။", message.chat.id, msg.message_id)

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
