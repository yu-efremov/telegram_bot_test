from flask import Flask, request, render_template
from threading import Thread
import matplotlib.pyplot as plt, mpld3
# import time
# import requests

# InfluxDB part
import os
from influxdb_client_3 import InfluxDBClient3, Point

# app part
app = Flask('')


@app.route('/')
def home():
  #return "I'm alive"
  # InfluxDB part
  bucket = "test_YE"
  database = "test_YE"
  org = "IRM"
  token = os.environ['InfluxDB_token']
  # Store the URL of your InfluxDB instance
  host="https://eu-central-1-1.aws.cloud2.influxdata.com"
  data_measurement = "test/temperature"
  data_tags = ["test/temperature", "test/temperature2"]
  InfluxDBclient = InfluxDBClient3(host=host, token=token, org=org,  database=database)
  # tabledata = InfluxDBclient.query(
  #   "SELECT {0} from {1}".format(", ".join(data_tags), data_measurement)
  # )
  tabledata = InfluxDBclient.query(
      query="SELECT * FROM 'Data'",
      language="sql"
  )
  print(tabledata)
  # data_points = []
  # for measurement, tags in tabledata.keys():
  #   for p in tabledata.get_points(measurement=measurement, tags=tags):
  #       data_points.append(p)
  # print(data_points)
  fig = plt.figure()
  x_vals = []
  y_vals = []
  label = ""
  # for record in tabledata:
  #   print('HereR')
  #   # print(record)
  #   print(record["_value"])
  #   # y_vals.append(record["_value"])
  #   # x_vals.append(record["_time"])
  #   # label = record["_measurement"]
  #   y_vals.append(record["_value"])
  #   x_vals.append(record["_time"])
  #   label = record["_measurement"]
  # plt.plot(x_vals, y_vals, label=label)
  x_vals = tabledata['time']
  y_vals = tabledata['test/temperature']
  plt.plot(x_vals, y_vals)
  grph = mpld3.fig_to_html(fig)
  return render_template("home.html",
                         user_name = "user_name",
                         graph_code = grph)


@app.route("/favicon.ico")
def favicon():
  return url_for('static', filename='data:,')


def run():
  app.run(host='0.0.0.0', port=80)


def keep_alive():
  t = Thread(target=run)
  t.start()
