import os
from background import keep_alive  #импорт функции для поддержки работоспособности
import telebot
import time
import paho.mqtt.client as mqtt
from threading import Thread, Event
from myBot import bot # бот в отдельном thread
# import json

# bot = telebot.TeleBot(os.environ['telegram_bot_API_token'])


@bot.message_handler(commands=['temp'])
def handle_temp(message):
  if 'test/temperature' in alldata:
    del alldata['test/temperature']
  readmqtt()
  time.sleep(2)
  # bot.reply_to(message, 'Привет! Я бот.')
  if 'test/temperature' in alldata:
    bot.reply_to(message, alldata['test/temperature'])
  else:
    bot.reply_to(message, 'Возможно нет подключения')


my_event = Event()
my_event.clear()


@bot.message_handler(commands=['start'])
def handle_start(message):
  global thread1, my_event
  thread1 = Thread(target=main4(message, my_event), args=(
      message,
      my_event,
  ))
  thread1.start()
  my_event.clear()


@bot.message_handler(commands=['stop'])
def handle_stop(message):
  global my_event
  if 'thread1' in globals():
    print('thread1 in globals')
    global thread1
    my_event.set()
    # bot.send_message(message.from_user.id, text='Мониторинг остановлен')
    bot.reply_to(message, text='Мониторинг остановлен')
  else:
    # global my_event
    print('thread1 not found')
    my_event.set()
    # bot.send_message(message.from_user.id, text='Мониторинг остановлен')
    bot.reply_to(message, text='Мониторинг остановлен')
    # thread1.join()


@bot.message_handler(content_types=['text'])
def get_text_message(message):
  bot.send_message(message.from_user.id, message.text)


# echo-функция, которая отвечает на любое текстовое сообщение таким же текстом

def main4(message, event_state):  #infinite messaging loop
  print('Бот4 запущен')
  # bot.send_message(message.from_user.id, text='Запущен мониторинг')
  bot.reply_to(message, 'Запущен мониторинг')
  while True:
    if event_state.is_set():
      break
    if 'test/temperature' in alldata:
      del alldata['test/temperature']
    readmqtt()
    time.sleep(5)
    if 'test/temperature' in alldata:
      # pass
      # bot.send_message(message.from_user.id, alldata['test/temperature'])
      bot.reply_to(message, alldata['test/temperature'])
    else:
      bot.reply_to(message, 'Возможно нет подключения')
    time.sleep(60*30-5)


# MQTT process
def on_connect(client, userdata, flags, rc):
  client.subscribe('test/temperature')
  global flag_connected
  flag_connected = 1
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
  alldata.update({'counter': alldata['counter'] + 1})


def readmqtt():
  client = mqtt.Client()
  client.username_pw_set(username=os.environ['mqtt_username'], password='')
  client.on_connect = on_connect
  client.on_message = on_message
  client.connect('mqtt.beebotte.com', 1883, 60)
  client.loop_start()  # это лучше
  # client.loop_forever()  # c этим виснет


# if __name__ == '__main__': проблемы в render
flag_connected = 0
alldata = {}
alldata['counter'] = 0
keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
print('Here1')
readmqtt()
print('Here2')
# bot.polling(non_stop=True, interval=0)  #запуск бота
# bot.infinity_polling(none_stop=True)
