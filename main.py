import telebot
import yt_dlp
import os
import re
from telebot import types

TOKEN = "8708016300:AAEbKbvt6lW84vD4OAFFwIDI1PmbYbnpAkY"
bot = telebot.TeleBot(TOKEN)
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "📥 Link yuboring, men videoni topaman!")

@bot.message_handler(func=lambda m: True)
def get_link(message):
    url = message.text.strip()
    if not re.match(r'https?://', url):
        bot.reply_to(message, "❌ Toʻgʻri havola yuboring.")
        return

    # Video ma'lumotlarini olish (yuklamasdan)
    msg = bot.reply_to(message, "🔍 Video qidirilmoqda...")
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            # Tugma yaratamiz (callback_data ichiga url ni yashiramiz)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📥 Yuklab olish", callback_data=f"down:{url}"))
            
            bot.edit_message_text(f"🎬 Topildi: {title}", message.chat.id, msg.message_id, reply_markup=markup)
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("down:"))
def download_callback(call):
    url = call.data.split(":")[1]
    bot.answer_callback_query(call.id, "⏳ Yuklanmoqda, kuting...")
    
    try:
        ydl_opts = {'format': 'best', 'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as f:
            bot.send_video(call.message.chat.id, f)
        os.remove(filename)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xato: {e}")

bot.infinity_polling()
