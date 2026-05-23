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
            
            markup = types.InlineKeyboardMarkup()
            # Callback ma'lumotlarini aniqroq qildik
            markup.add(types.InlineKeyboardButton("🎬 Videoni yuklash (MP4)", callback_data=f"vid|{url}"))
            markup.add(types.InlineKeyboardButton("🎵 Musiqani yuklash (MP3)", callback_data=f"mus|{url}"))
            
            bot.edit_message_text(f"🎬 Topildi: {title}\nQaysi formatda yuklaymiz?", message.chat.id, msg.message_id, reply_markup=markup)
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def download_callback(call):
    # Callback ma'lumotini "|" belgisi bilan ajratib olamiz
    data = call.data.split("|")
    if len(data) != 2:
        return
    
    action, url = data
    bot.answer_callback_query(call.id, "⏳ Yuklanmoqda, kuting...")
    
    # Yuklash sozlamalari
    ydl_opts = {'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s'}
    
    if action == "mus":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'best'
        
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Agar mp3 bo'lsa, kengaytmasi o'zgaradi
            if action == "mus":
                filename = filename.rsplit('.', 1)[0] + '.mp3'
        
        with open(filename, 'rb') as f:
            if action == "mus":
                bot.send_audio(call.message.chat.id, f)
            else:
                bot.send_video(call.message.chat.id, f)
        os.remove(filename)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xato: {e}")

bot.infinity_polling()
