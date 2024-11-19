from flask import Flask, request, render_template
from threading import Thread
import matplotlib.pyplot as plt, mpld3
from matplotlib.dates import DateFormatter
# import mpld3
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
  database = "test_YE"  # bucket
  org = "IRM"
  token = os.environ['InfluxDB_token']
  # Store the URL of your InfluxDB instance
  host="https://eu-central-1-1.aws.cloud2.influxdata.com"
  measurements_name = "temperaturenew"  # data
  # data_measurement = "test/temperature"
  #data_tags = ["test/temperature", "test/temperature2", "test/temperature3"]
  # data_tags = ["test/temperature3", "SensorNik"]
  data_tags = ["SensorTypeC", "SensorNik"]
  InfluxDBclient = InfluxDBClient3(host=host, token=token, org=org,  database=database)
  # tabledata = InfluxDBclient.query(
  #   "SELECT {0} from {1}".format(", ".join(data_tags), data_measurement)
  # )
  query_str = "SELECT * FROM " + measurements_name #  + " WHERE 'location' IN ('Location')"
  print(query_str)
  tabledata = InfluxDBclient.query(
      # query="SELECT * FROM " + measurements_name,
      query=query_str,
      language="sql"
  )
  print(tabledata)
  # data_points = []
  # for measurement, tags in tabledata.keys():
  #   for p in tabledata.get_points(measurement=measurement, tags=tags):
  #       data_points.append(p)
  # print(data_points)
  # fig = plt.figure()
  fig, ax = plt.subplots()
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
  data_tags = tabledata.column_names
  print("Table names")
  print(data_tags)
  data_tags.remove('time')
  data_tags.remove('SSID')
  data_tags.remove('device')
  data_tags.remove('location')
  print(data_tags)
  for ii in range(0,len(data_tags)):
    x_vals = tabledata['time']
    y_vals = tabledata[data_tags[ii]]
    ax.plot(x_vals, y_vals, label=data_tags[ii])  # plt.plot

  myFmt = DateFormatter(('%HH:%MM'))  # remove AM/PM
  ax.xaxis.set_major_formatter(myFmt)
  fig.autofmt_xdate()  # Rotate date labels automatically
  plt.legend(loc="upper left")
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
