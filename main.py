import telebot
import yt_dlp
import os
import re
import uuid
from telebot import types

TOKEN = "8708016300:AAF-uYjYETmSppYGUKu4mf6Hb8l2BlItiH0"
bot = telebot.TeleBot(TOKEN)
DOWNLOAD_FOLDER = "downloads"

# Linklarni vaqtincha saqlash uchun lug'at (Memory storage)
url_storage = {}

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

    # Unikal ID yaratamiz
    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = url

    msg = bot.reply_to(message, "🔍 Video ma'lumotlari olinmoqda...")
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            
            markup = types.InlineKeyboardMarkup()
            # Tugmalarga faqat qisqa ID ni yozamiz
            markup.add(types.InlineKeyboardButton("🎬 Videoni yuklash (MP4)", callback_data=f"vid|{link_id}"))
            markup.add(types.InlineKeyboardButton("🎵 Musiqani yuklash (MP3)", callback_data=f"mus|{link_id}"))
            
            bot.edit_message_text(f"🎬 Topildi: {title}\nQaysi formatda yuklaymiz?", message.chat.id, msg.message_id, reply_markup=markup)
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def download_callback(call):
    data = call.data.split("|")
    if len(data) != 2:
        return
    
    action, link_id = data
    url = url_storage.get(link_id)
    
    if not url:
        bot.answer_callback_query(call.id, "❌ Link eskirgan, qaytadan yuboring!")
        return

    bot.answer_callback_query(call.id, "⏳ Yuklanmoqda, kuting...")
    
    ydl_opts = {'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s'}
    
    if action == "mus":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    else:
        ydl_opts['format'] = 'best'
        
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
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
