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

    msg = bot.reply_to(message, "🔍 Video ma'lumotlari olinmoqda...")
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            
            # Ikkita tugma yaratamiz
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎬 Videoni yuklash (MP4)", callback_data=f"down_v:{url}"))
            markup.add(types.InlineKeyboardButton("🎵 Musiqani yuklash (MP3)", callback_data=f"down_a:{url}"))
            
            bot.edit_message_text(f"🎬 Topildi: {title}\nQaysi formatda yuklaymiz?", message.chat.id, msg.message_id, reply_markup=markup)
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("down_"))
def download_callback(call):
    action, url = call.data.split(":")
    bot.answer_callback_query(call.id, "⏳ Yuklanmoqda, kuting...")
    
    # Agar MP3 tanlansa formatni o'zgartiramiz
    ydl_opts = {'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s'}
    if action == "down_a":
        ydl_opts['format'] = 'bestaudio/best'
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as f:
            if action == "down_a":
                bot.send_audio(call.message.chat.id, f)
            else:
                bot.send_video(call.message.chat.id, f)
        os.remove(filename)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xato: {e}")

print("Bot ishladi ✅")
bot.infinity_polling()
