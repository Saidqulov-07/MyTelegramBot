import telebot

TOKEN = "8708016300:AAF-uYjYETmSppYGUKu4mf6Hb8l2BlItiH0"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Bot ishlayapti ✅")

bot.infinity_polling()
