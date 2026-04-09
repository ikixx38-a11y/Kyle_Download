import os
import telebot
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# Bot API Token
TOKEN = os.getenv('8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g')
bot = telebot.TeleBot(TOKEN)

# TikTok Downloader Function
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

# --- Telegram Bot Logic ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "TikTok link ပို့ပေးပါ၊ Watermark မပါဘဲ ဒေါင်းပေးမယ်။")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def handle_msg(message):
    temp = bot.reply_to(message, "⌛ ခဏစောင့်ပါ...")
    try:
        file_path = download_tiktok(message.text)
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove(file_path)
        bot.delete_message(message.chat.id, temp.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, temp.message_id)

# --- Render အတွက် Web Server အသေးစားလေး ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_web_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Web Server ကို Thread တစ်ခုနဲ့ အရင် Run မယ် (Render အတွက်)
    Thread(target=run_web_server).start()
    # Bot ကို Polling လုပ်မယ်
    bot.infinity_polling()
