import os
from background import keep_alive  #импорт функции для поддержки работоспособности
import time
import paho.mqtt.client as mqtt
# from threading import Thread, Event
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
# import json

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.environ['telegram_bot_API_token'])
# Диспетчер
dp = Dispatcher()

#def bot_check():
#    return bot.get_me()


# Хэндлер на команду /start
@dp.message(Command("start1"))
async def cmd_start1(message: types.Message):
  await message.answer("Hello!")
  await bot.send_message(chat_id=message.from_user.id,
                         text="Some info")


@dp.message(Command("temp"))
async def cmd_temp(message: types.Message):
  if 'test/temperature' in alldata:
    del alldata['test/temperature']
  readmqtt()
  await asyncio.sleep(2)
  # bot.reply_to(message, 'Привет! Я бот.')
  if 'test/temperature' in alldata:
    await message.answer(alldata['test/temperature'])
  else:
    await message.answer("Возможно нет подключения")


my_event = asyncio.Event()
my_event.clear()

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
  await bot.send_message(chat_id=message.from_user.id,
                         text="Info will be there")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  # loop = asyncio.get_event_loop()
  # loop.run_until_complete(main4(message, my_event))
  # await bot.send_message(chat_id=message.from_user.id,
  #    text="Запущен мониторинг")
  await message.answer("Запущен мониторинг")
  my_event.clear()
  while True:
    print('Бот работает')
    if my_event.is_set():  # If flag is set then break the loop
      print('Бот остановлен')
      break
    await asyncio.sleep(5)  # Wait 0.5 s between the requests
    # await bot.send_message(chat_id=message.from_user.id,
    #      text="Запущен мониторинг52")
    if 'test/temperature' in alldata:
      del alldata['test/temperature']
    readmqtt()
    await asyncio.sleep(5)
    if 'test/temperature' in alldata:
      # pass
      print(alldata['test/temperature'])
      # await bot.send_message(message.from_user.id, alldata['test/temperature'])
      await message.answer(alldata['test/temperature'])
    else:
      await message.answer("Возможно нет подключения")
    await asyncio.sleep(60*30-5)  # Wait 0.5 s between the requests

@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
  # loop = asyncio.get_event_loop()
  # loop.run_until_complete(main4(message, my_event))
  my_event.set()
  # await bot.send_message(chat_id=message.from_user.id,
  #                        text="Мониторинг остановлен")
  await message.answer("Мониторинг остановлен")


dp.message.register(cmd_temp, Command("temp"))
dp.message.register(cmd_info, Command("info"))
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_stop, Command("stop"))


async def main5(message, event_state):
  print('Бот5 запущен')
  await bot.send_message(chat_id=message.from_user.id,
                         text="Запущен мониторинг51")
  while 1:
    print('Бот работает')
    await asyncio.sleep(5)  # Wait 0.5 s between the requests
    await bot.send_message(chat_id=message.from_user.id,
                           text="Запущен мониторинг52")
    if event_state.is_set():  # If flag is set then break the loop
      print('Бот остановлен')
      break


async def main():
  await dp.start_polling(bot)


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
asyncio.run(main())
