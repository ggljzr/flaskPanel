#!/usr/bin/python

#simple flask server for reading dht11 sensor and fetching data

import sys
import os
import time
import Adafruit_DHT

from flask import Flask
from flask import render_template

app = Flask(__name__)

sensor = 11 #using DHT11 sensor
pin = 13 #connected to pin 13

@app.route('/')
def hello_world():
	(hum, temp) = Adafruit_DHT.read_retry(sensor, pin)
	date = os.popen('date', 'r').read()
	uptime = os.popen("uptime | awk -F, {'print $1$2'}", 'r').read()
	uptime = uptime[10:].replace('  ', ' ') #remove date and redundant space
	loadavg = os.popen('cat /proc/loadavg', 'r').read()
	return render_template('index.html', uptime=uptime,
					     date=date,
					     loadavg=loadavg,
					     hum=hum,temp=temp)

@app.route('/getTemp')
def get_temp():
	(hum, temp) = Adafruit_DHT.read_retry(sensor, pin) 

	if temp is not None and hum is not None:
		return '{"temp" : ' + str(temp) + ',"hum" : ' + str(hum) + '}'
	else:
		return '{"temp" : "none" , "hum" : "none"}'

@app.route('/ipconf')
def ipconf():
	return os.popen('ifconfig', 'r').read()

@app.route('/uptime')
def uptime():
	return os.popen('uptime', 'r').read()

if __name__ == '__main__':
	app.run(host='raspberrypi.local')
