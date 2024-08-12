from flask import Flask
from flask import request
from threading import Thread
import time
import requests
import myBot # бот в отдельном thread


app = Flask('')

@app.route('/')
def home():
  return "I'm alive"

@app.route("/favicon.ico")
def favicon():
    return url_for('static', filename='data:,')

def run():
  app.run(host='0.0.0.0', port=80)

def keep_alive():
  t = Thread(target=run)
  t.start()

def home():
  if myBot.bot_check():
      return "I'm alive and bot is checked"
  else:
      print("Problems with bot")
