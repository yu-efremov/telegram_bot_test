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

from influxdb_client_3 import InfluxDBClient3
from sensors_dict import sensors_dict  # for monitoring
sensors_list = list(sensors_dict.keys())
# import pandas as pd
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
      as_key_value("Текущая температура", "/get_temp"),
      as_key_value("Запустить мониторинг", "/start_monitoring"),
      as_key_value("Остановить мониторинг", "/stop"),
      as_key_value("Периодичность мониторинга", "/settimer"),
      as_key_value("Сайт мониторинга", "https://telegram-bot-test-yjoz.onrender.com"),
      marker="  ",
  ),
  )
  await message.answer(**content.as_kwargs())
  # await bot.send_message(chat_id=message.from_user.id, text="Some info")


@dp.message(Command("get_temp"))
async def cmd_temp(message: types.Message):
  msgR = await message.answer("Пожодите 10 секунд для сбора информации")
  for i, (k, v) in enumerate(sensors_dict.items()):
    if k in alldata:
      del alldata[k]
  print(message.chat.id)

  read_influxdb()
  # await asyncio.sleep(12)  # wait in readmqtt
  # bot.reply_to(message, 'Привет! Я бот.')
  print(alldata)
  response_string = ''
  for i, (k, v) in enumerate(sensors_dict.items()):
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

@dp.message(Command("get_temp_all"))
async def cmd_temp2(message: types.Message):
  msgR = await message.answer("Пожодите 10 секунд для сбора информации")
  for i, (k, v) in enumerate(tags_dict.items()):
    if k in alldata:
      del alldata[k]
  print(message.chat.id)
  print(data_tags)
  read_influxdb()
  # await asyncio.sleep(12)  # wait in readmqtt
  # bot.reply_to(message, 'Привет! Я бот.')
  print(alldata)
  response_string = ''
  for i, (k, v) in enumerate(tags_dict.items()):
    if k in alldata:
      response_string = response_string + v + ": " + alldata[k] + "\n"
      # await message.answer(v + ": " + alldata[k])
    else:
      response_string = response_string + v + ": Нет подключения" + "\n"
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


@dp.message(Command("start_monitoring"))
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
      for i, (k, v) in enumerate(tags_dict.items()):
        if k in alldata:
          del alldata[k]
      read_influxdb()
      # await asyncio.sleep(11)  # wait already in readmqtt
      response_string = ""
      for i, (k, v) in enumerate(sensors_dict.items()):
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
dp.message.register(cmd_temp, Command("start_monitoring"))
dp.message.register(cmd_temp2, Command("start_monitoring_all"))
dp.message.register(cmd_info, Command("info"))
dp.message.register(cmd_start, Command("get_temp"))
dp.message.register(cmd_stop, Command("stop"))
dp.message.register(cmd_settimer, Command("settimer"))
dp.message.register(all_other, Command("all_other"))



async def main():
  await dp.start_polling(bot)


# InfluxDB part
bucket = "test_YE"
database = "test_YE"
org = "IRM"
token = os.environ['InfluxDB_token']
# Store the URL of your InfluxDB instance
host="https://eu-central-1-1.aws.cloud2.influxdata.com"

InfluxDBclient = InfluxDBClient3(host=host, token=token, org=org,  database=database)
print('Connected to InfluxDBclient')

measurements_name = "temperaturenew"
query_str = f"SELECT * as val FROM {measurements_name} WHERE time >= now() - 2m"
tabledata = InfluxDBclient.query(query=query_str, language="influxql")
data_tags = tabledata.column_names
print("Table names")
data_tags.remove('time')
data_tags.remove('SSID')
data_tags.remove('device')
data_tags.remove('location')
data_tags.remove('iox::measurement')
print(data_tags)
tags_dict = dict(zip(data_tags, data_tags))
# data_tags = ["SensorTypeC", "SensorNikul"]
# tags_dict = {
#   "SensorTypeC": "Сенсор1",
#   "SensorNikul": "сенсор_никул",
# }

# tags = []
# for i, (k, v) in enumerate(tags_dict.items()):
#   tags.append((k, i))
#   print(i, k, v)

def read_influxdb():
  measurements_name = "temperaturenew"
#  tabledata = InfluxDBclient.query(
#    query="SELECT * FROM " + measurements_name +
#    # "WHERE time >= now() - interval '1 minute'",
#    "WHERE time >= now() - 2 m",
#    language="influxql"
#  )
  query_str = f"SELECT * as val FROM {measurements_name} WHERE time >= now() - 2m"
#  tabledata = InfluxDBclient.query(query='''SELECT * as val
#  FROM temperature
#  WHERE time >= now() - 1m''', language="influxql")
  tabledata = InfluxDBclient.query(query=query_str, language="influxql")
  print(tabledata)
  data_tags = tabledata.column_names
  print("Table names")
  data_tags.remove('time')
  data_tags.remove('SSID')
  data_tags.remove('device')
  data_tags.remove('location')
  data_tags.remove('iox::measurement')
  print(data_tags)
  tags_dict = dict(zip(data_tags, data_tags))
  
  for ii in range(0,len(data_tags)):
    x_vals = tabledata['time']
    y_vals = tabledata[data_tags[ii]]
    y_vals = y_vals.drop_null()
    print(y_vals)
    # df = tabledata.to_pandas()
    # print(df)
    # ctemp = df['val'].iloc[-1].values
    if len(y_vals)>0:
      alldata.update({str(data_tags[ii]): str(y_vals[-1])})
      print(y_vals[-1])
    else:
      print(data_tags[ii] + " - Нет подключения!")


# if __name__ == '__main__': проблемы в render
flag_connected = 0
alldata = {}
alldata['counter'] = 0
alldata['monitoring_time'] = int(10 * (60))  # default 10 mins
keep_alive()  #запускаем flask-сервер в отдельном потоке. Подробнее ниже...
print('Here1')
read_influxdb()
print('Here2')
asyncio.run(main())
