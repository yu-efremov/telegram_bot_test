import os
from background import keep_alive #импорт функции для поддержки работоспособности
import pip
pip.main(['install', 'pytelegrambotapi'])
import telebot
import time
import paho.mqtt.client as mqtt

bot = telebot.TeleBot(os.environ['telegram_bot_API_token'])


@bot.message_handler(content_types=['text'])
def get_text_message(message):
  bot.send_message(message.from_user.id, message.text)


# echo-функция, которая отвечает на любое текстовое сообщение таким же текстом

keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
bot.polling(non_stop=True, interval=0)  #запуск бота
