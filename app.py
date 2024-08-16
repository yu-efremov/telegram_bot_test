# from threading import Thread, Event
import asyncio
import logging
import os

import paho.mqtt.client as mqtt
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from background import keep_alive  #импорт функции для поддержки работоспособности

# import json

monitoring_time = 60 * (60)  # seconds
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.environ['telegram_bot_API_token'])
# Диспетчер
dp = Dispatcher()

admin_ID = os.environ['admin_telegramID']
admin_username = os.environ['admin_telegramUsername']
group_telegramID = os.environ['group_telegramID']
#admin_ID = int(admin_ID)
#def bot_check():
#    return bot.get_me()


# Хэндлер на команду /start
@dp.message(Command("start1"))
async def cmd_start1(message: types.Message):
  await message.answer("Hello!")
  await bot.send_message(chat_id=message.from_user.id, text="Some info")


@dp.message(Command("temp"))
async def cmd_temp(message: types.Message):
  msgR = await message.answer("Пожодите 10 секунд для сбора информации")
  for i, (k, v) in enumerate(topic_dict.items()):
    if k in alldata:
      del alldata[k]
  readmqtt()
  print(message.chat.id)
  await asyncio.sleep(11)
  # bot.reply_to(message, 'Привет! Я бот.')
  print(alldata)
  response_string = ''
  for i, (k, v) in enumerate(topic_dict.items()):
    if k in alldata:
      response_string = response_string + v + ": " + alldata[k] + "\n"
      # await message.answer(v + ": " + alldata[k])
    else:
      response_string = response_string + v + ": Нет подключения" + "\n"
      # await message.answer(v + ": Нет подключения")
  # await message.answer(response_string)
  # print(msgR)
  # print(msgR.message_id)
  # messageR_id = msgR["message_id"]
  await bot.edit_message_text( 
    text=response_string,
    chat_id=message.chat.id,
    message_id=msgR.message_id)


my_event = asyncio.Event()
my_event.clear()


@dp.message(Command("info"))
async def cmd_info(message: types.Message):
  await bot.send_message(chat_id=message.from_user.id,
                         text="Info will be there")
  await message.answer("Команда доступна только администратору " +
                       f"@{admin_username}")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  # loop = asyncio.get_event_loop()
  # loop.run_until_complete(main4(message, my_event))
  # await bot.send_message(chat_id=message.from_user.id,
  #    text="Запущен мониторинг")
  print(message.from_user.id)
  if str(message.from_user.id) == admin_ID:
    await message.answer("Запущен мониторинг")
    UsrInfo = await bot.get_chat_member(chat_id=admin_ID, user_id=admin_ID)
    print(UsrInfo)
    print(UsrInfo.user.username)
    my_event.clear()
    while True:
      print('Бот работает')
      if my_event.is_set():  # If flag is set then break the loop
        print('Бот остановлен')
        break
      await asyncio.sleep(5)  # Wait 0.5 s between the requests
      for i, (k, v) in enumerate(topic_dict.items()):
        if k in alldata:
          del alldata[k]
      readmqtt()
      await asyncio.sleep(11)
      response_string = ""
      for i, (k, v) in enumerate(topic_dict.items()):
        if k in alldata:
          response_string = response_string + v + ": " + alldata[k] + "\n"
          # await message.answer(v + ": " + alldata[k])
        else:
          response_string = response_string + v + ": Нет подключения" + "\n"
          # await message.answer(v + ": Нет подключения")
          await bot.send_message(chat_id=group_telegramID, text=v + ": Нет подключения!!!!")
      await message.answer(response_string)
      await asyncio.sleep(monitoring_time)  # Wait some s between the requests
  else:
    await message.answer("Команда доступна только администратору " +
                         f"@{admin_username}"
                         )  # message.from_user.url message.from_user.username
    # chat_id = message.chat.id
    # button_url = f'tg://openmessage?user_id={chat_id}'
    # markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton(text=button_text, url=button_url))
    # await bot.send_message(admin_id, text=f'{chat_id}', reply_markup=markup)
    # await bot.send_message(chat_id,
    #     text=f"Hello, <b>{html.quote(message.from_user.full_name)}!</b>",
    #     parse_mode=ParseMode.HTML
    # )


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
  if str(message.from_user.id) == admin_ID:
    my_event.set()
    await message.answer("Мониторинг остановлен")
    # await bot.send_message(chat_id=message.from_user.id,
    #                        text="Мониторинг остановлен")
  else:
    await message.answer("Команда доступна только администратору " +
                         f"@{admin_username}")


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

topic_dict = {
    "test/temperature": "сенсор1",
    "test/temperature2": "сенсор2",
}

topics = []
for i, (k, v) in enumerate(topic_dict.items()):
  topics.append((k, i))
  print(i, k, v)


def on_connect(client, userdata, flags, rc):
  global topics, flag_connected
  print(topics)
  client.subscribe(topics)
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
asyncio.run(main())
