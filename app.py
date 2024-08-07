import os
from background import keep_alive  #импорт функции для поддержки работоспособности
import telebot
import time
import paho.mqtt.client as mqtt
# import json

bot = telebot.TeleBot(os.environ['telegram_bot_API_token'])
@bot.message_handler(commands=['temp'])
def handle_start(message):
  readmqtt()
  # bot.reply_to(message, 'Привет! Я бот.')
  bot.reply_to(message, alldata['test/temperature'])


@bot.message_handler(content_types=['text'])
def get_text_message(message):
  bot.send_message(message.from_user.id, message.text)


# echo-функция, которая отвечает на любое текстовое сообщение таким же текстом


# MQTT process
def on_connect(client, userdata, flags, rc):
  client.subscribe('test/temperature')
  print('Connected')


def on_message(client, userdata, msg):
  m_decode = str(msg.payload.decode("utf-8", "ignore"))
  # print("data Received type", type(m_decode))
  print("data Received", m_decode)
  # userdata.append(m_decode)
  #if len(userdata) >= 2:
  # it's possible to stop the program by disconnecting
  client.disconnect()
  # m_in = json.loads(m_decode)  # decode json data
  # print(type(m_in))
  # print("method is = ", m_in["method"])  # <-- shall be m_in["method"]
  alldata.update({str(msg.topic): str(m_decode)})


def readmqtt():
  client = mqtt.Client()
  client.username_pw_set(username=os.environ['mqtt_username'], password='')
  client.on_connect = on_connect
  client.on_message = on_message
  client.connect('mqtt.beebotte.com', 1883, 60)
  client.loop_start()  # это лучше
  # client.loop_forever()  # c этим виснет


alldata = {}
keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
print('Here1')
readmqtt()
print('Here2')
bot.polling(non_stop=True, interval=0)  #запуск бота
