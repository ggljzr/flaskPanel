#!/usr/bin/python

#simple flask server for reading dht11 sensor and fetching data

import sys
import os
import time
import Adafruit_DHT
import string

from flask import Flask
from flask import render_template

app = Flask(__name__)

sensor = 11 #using DHT11 sensor
pin = 13 #connected to pin 13

#primitive ifconfig parser
def parse_ifconfig(interface):
	retval = []
	
	#try to find hwaddr
	hwaddr = os.popen('ifconfig ' + str(interface) + " | grep HWaddr | awk -F' ' '{print $5}' ", 'r').read()
	if hwaddr == '' or hwaddr.isspace():
		hwaddr = 'HWaddr:none'
	else:
		hwaddr = 'HWaddr:' + hwaddr

	retval.append(hwaddr)

	for i in range(2,5):
		info = os.popen('ifconfig ' + str(interface) + 
				" | grep inet | awk -F' ' '{print $" + str(i) +
				" }'", 'r').read()
		if info == '' or info.isspace():
			continue
		else:
			retval.append(info)
	
	return retval

#parsing df output
def parse_df(device):
	return os.popen('df -h ' + str(device) + ' | tail -n 1', 'r').read().split()

@app.route('/')
def hello_world():
	(hum, temp) = Adafruit_DHT.read_retry(sensor, pin)
	date = os.popen('date', 'r').read()
	uptime = os.popen("uptime | awk -F, {'print $1$2'}", 'r').read()
	uptime = uptime[10:].replace('  ', ' ') #remove date and redundant space
	loadavg = os.popen('cat /proc/loadavg', 'r').read()

	eth0_data = parse_ifconfig('eth0')
	lo_data = parse_ifconfig('lo')

	root_info = parse_df('/dev/root');
	sda1_info = parse_df('/dev/sda1');
	return render_template('index.html', uptime=uptime,
					     date=date,
					     loadavg=loadavg,
					     root_info=root_info,
					     sda1_info=sda1_info,
					     eth0_data=eth0_data,
					     lo_data = lo_data,
					     hum=hum,temp=temp)

@app.route('/getTemp')
def get_temp():
	(hum, temp) = Adafruit_DHT.read_retry(sensor, pin) 

	if temp is not None and hum is not None:
		return '{"temp" : ' + str(temp) + ',"hum" : ' + str(hum) + '}'

	return '{"temp" : "none" , "hum" : "none"}'

@app.route('/ipconf')
def ipconf():
	return os.popen('ifconfig', 'r').read()

@app.route('/uptime')
def uptime():
	return os.popen('uptime', 'r').read()
@app.route('/df')
def disks():
	return os.popen('df -h', 'r').read()

if __name__ == '__main__':
	app.run(host='raspberrypi.local')
