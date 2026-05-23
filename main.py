import telebot
import yt_dlp
import os
import uuid
from telebot import types

TOKEN = "8708016300:AAFnz31dVcNFaAD0MKgAGVBS1CQ7B0S0zwM"
bot = telebot.TeleBot(TOKEN)
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Linklarni saqlash
url_storage = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "📥 Link yuboring, men videoni va musiqani yuklab beraman!")

@bot.message_handler(func=lambda m: True)
def get_link(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Toʻgʻri havola yuboring.")
        return

    link_id = str(uuid.uuid4())[:8]
    url_storage[link_id] = url

    msg = bot.reply_to(message, "⏳ Yuklanmoqda, kuting...")
    
    try:
        ydl_opts = {'outtmpl': f'{DOWNLOAD_FOLDER}/{link_id}.%(ext)s', 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Tugma yaratish
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎵 Musiqani yuklash (MP3)", callback_data=f"mus|{link_id}"))
            
            # Videoni yuborish
            with open(filename, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=f"🎬 {info.get('title')}", reply_markup=markup)
            
            os.remove(filename)
            bot.delete_message(message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mus"))
def download_music(call):
    link_id = call.data.split("|")[1]
    url = url_storage.get(link_id)
    
    if not url:
        bot.answer_callback_query(call.id, "❌ Link eskirgan!")
        return

    bot.answer_callback_query(call.id, "🎵 Musiqa tayyorlanmoqda...")
    
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/{link_id}.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
        
        with open(filename, 'rb') as f:
            bot.send_audio(call.message.chat.id, f)
        os.remove(filename)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xato: {e}")

bot.infinity_polling()
