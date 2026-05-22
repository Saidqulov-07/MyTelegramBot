import telebot

TOKEN = "8708016300:AAEbKbvt6lW84vD4OAFFwIDI1PmbYbnpAkY"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Bot ishlayapti ✅")

bot.infinity_polling()