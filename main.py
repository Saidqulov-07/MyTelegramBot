import telebot
import yt_dlp
import os
import re

TOKEN = "8708016300:AAEbKbvt6lW84vD4OAFFwIDI1PmbYbnpAkY"

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "📥 Media Downloader Bot\n\n"
        "Link yuboring:\n"
        "• Instagram\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Facebook\n"
        "• Pinterest\n"
        "• Snapchat\n"
        "• Likee\n"
        "• Threads"
    )


@bot.message_handler(func=lambda m: True)
def download_media(message):

    url = message.text.strip()

    if not re.match(r'https?://', url):
        bot.reply_to(message, "❌ Havola yuboring")
        return

    loading_msg = bot.reply_to(message, "⏳ Yuklanmoqda...")

    try:

        # DOWNLOAD SETTINGS
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }

        # DOWNLOAD
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # DOWNLOADS papkasidan faylni topish
        files = os.listdir(DOWNLOAD_FOLDER)

        if not files:
            bot.send_message(message.chat.id, "❌ Media topilmadi")
            return

        latest_file = max(
            [os.path.join(DOWNLOAD_FOLDER, f) for f in files],
            key=os.path.getctime
        )

        # TELEGRAMGA YUBORISH
        with open(latest_file, 'rb') as media:

            # VIDEO
            if latest_file.endswith(('.mp4', '.mkv', '.webm')):
                bot.send_video(message.chat.id, media)

            # AUDIO
            elif latest_file.endswith(('.mp3', '.m4a')):
                bot.send_audio(message.chat.id, media)

            # OTHER FILES
            else:
                bot.send_document(message.chat.id, media)

        # STATUS MESSAGE DELETE
        bot.delete_message(message.chat.id, loading_msg.message_id)

        # FILE DELETE
        os.remove(latest_file)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xato:\n{e}")


print("Bot ishladi ✅")

bot.infinity_polling()