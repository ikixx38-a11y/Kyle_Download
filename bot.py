import os
import telebot
import yt_dlp

# သင့် Token ကို ဒီမှာ အတိအကျ ထည့်ပါ
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"
bot = telebot.TeleBot(TOKEN)

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
        bot.edit_message_text("❌ ဒေါင်းလုဒ်ဆွဲလို့မရပါ။ Link မှန်မမှန် ပြန်စစ်ပါ။", message.chat.id, wait.message_id)

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
