import telebot

TOKEN = "8708016300:AAFnz31dVcNFaAD0MKgAGVBS1CQ7B0S0zwM"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Bot ishlayapti ✅")

bot.infinity_polling()
