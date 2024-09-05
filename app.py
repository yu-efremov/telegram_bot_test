# from threading import Thread, Event
import asyncio
import logging
import os
import time
import paho.mqtt.client as mqtt
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)

from background import keep_alive  #импорт функции для поддержки работоспособности

from influxdb_client_3 import InfluxDBClient3, Point
# import json

# monitoring_time = int(10 * (60))  # seconds
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.environ['telegram_bot_API_token'])
# Диспетчер
dp = Dispatcher()

admin_ID = os.environ['admin_telegramID']
admin_username = os.environ['admin_telegramUsername']
group_telegramID = os.environ['group_telegramID']

#def bot_check():
#    return bot.get_me()


# Хэндлер на команду /start
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
  # await message.answer("Hello!")
  content = as_list(as_marked_section(
      Bold("Команды для бота:"),
      as_key_value("Текущая температура", "/start"),
      as_key_value("Запустить мониторинг", "/temp"),
      as_key_value("Остановить мониторинг", "/stop"),
      as_key_value("Периодичность мониторинга", "/settimer"),
      marker="  ",
  ),
  )
  await message.answer(**content.as_kwargs())
  # await bot.send_message(chat_id=message.from_user.id, text="Some info")


@dp.message(Command("temp"))
async def cmd_temp(message: types.Message):
  msgR = await message.answer("Пожодите 10 секунд для сбора информации")
  for i, (k, v) in enumerate(topic_dict.items()):
    if k in alldata:
      del alldata[k]
  print(message.chat.id)
  readmqtt()
  # await asyncio.sleep(12)  # wait in readmqtt
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
  await bot.edit_message_text(text=response_string,
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
  monitoring_time = alldata['monitoring_time']  # seconds
  print(message.from_user.id)
  if str(message.from_user.id) == admin_ID:
    await message.answer(f"Запущен мониторинг с частотой раз в {monitoring_time/60} минут")
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
      # await asyncio.sleep(11)  # wait already in readmqtt
      response_string = ""
      for i, (k, v) in enumerate(topic_dict.items()):
        if k in alldata:
          response_string = response_string + v + ": " + alldata[k] + "\n"
          # await message.answer(v + ": " + alldata[k])
        else:
          response_string = response_string + v + ": Нет подключения" + "\n"
          # await message.answer(v + ": Нет подключения")
          await bot.send_message(chat_id=group_telegramID,
                                 text=v + ": Нет подключения!!!!")
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


timerdict = {}


@dp.message(Command("settimer"))
async def cmd_settimer(message: types.Message, command: CommandObject):
  if str(message.from_user.id) == admin_ID:
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
      await message.answer("Ошибка: не переданы аргументы")
      return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
      delay_time = command.args.split(" ", maxsplit=1)
      alldata.update({"monitoring_time": int(delay_time[0]) * 60})
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
      await message.answer("Ошибка: неправильный формат команды. Пример:\n"
                           "/settimer <time> <message>")
      return
    await message.answer("Таймер добавлен!\n"
                         # f"Время: {delay_time}\n"
                         f"Время: {alldata['monitoring_time']/60} мин\n")
  else:
    await message.answer("Команда доступна только администратору " +
                         f"@{admin_username}")

@dp.message() # для всего остального
async def all_other(message: types.Message):
  await message.answer("Для получения информации о существующих командах введите /help")

dp.message.register(cmd_start, Command("help"))
dp.message.register(cmd_temp, Command("temp"))
dp.message.register(cmd_info, Command("info"))
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_stop, Command("stop"))
dp.message.register(cmd_settimer, Command("settimer"))
dp.message.register(all_other, Command("all_other"))


# async def main5(message, event_state):
#   print('Бот5 запущен')
#   await bot.send_message(chat_id=message.from_user.id,
#                          text="Запущен мониторинг51")
#   while 1:
#     print('Бот работает')
#     await asyncio.sleep(5)  # Wait 0.5 s between the requests
#     await bot.send_message(chat_id=message.from_user.id,
#                            text="Запущен мониторинг52")
#     if event_state.is_set():  # If flag is set then break the loop
#       print('Бот остановлен')
#       break


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
  # client.disconnect()
  # m_in = json.loads(m_decode)  # decode json data
  # print(type(m_in))
  # print("method is = ", m_in["method"])  # <-- shall be m_in["method"]
  alldata.update({str(msg.topic): str(m_decode)})
  alldata.update({'counter': alldata['counter'] + 1})
  point = (
    Point("Data")
    .tag("location", str(msg.topic))
    .field(str(msg.topic), float(alldata[str(msg.topic)]))
  )
  print(point)
  InfluxDBclient.write(database=database, record=point)


def readmqtt():
  client = mqtt.Client()
  client.username_pw_set(username=os.environ['mqtt_username'], password='')
  client.on_connect = on_connect
  client.on_message = on_message
  client.connect('mqtt.beebotte.com', 1883, 60)
  client.loop_start()  # это лучше
  startTime = time.time()
  runTime = 11
  while True:
    # mqttc.loop()
    currentTime = time.time()
    if (currentTime - startTime) > runTime:
      client.disconnect()
      break
  # client.loop_forever()  # c этим виснет

# InfluxDB part
bucket = "test_YE"
database="test_YE"
org = "IRM"
token = os.environ['InfluxDB_token']
# Store the URL of your InfluxDB instance
host="https://eu-central-1-1.aws.cloud2.influxdata.com"

InfluxDBclient = InfluxDBClient3(host=host, token=token, org=org)

# if __name__ == '__main__': проблемы в render
flag_connected = 0
alldata = {}
alldata['counter'] = 0
alldata['monitoring_time'] = int(10 * (60))  # default 10 mins
keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
print('Here11')
readmqtt()
print('Here2')
asyncio.run(main())
