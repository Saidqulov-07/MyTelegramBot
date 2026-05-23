import telebot

TOKEN = "8708016300:AAGNdWaBsU7hEnMXL3I2p8_a2yypPcHcdtY"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Bot ishlayapti ✅")

bot.infinity_polling()
