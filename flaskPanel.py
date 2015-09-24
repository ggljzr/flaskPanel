#!/usr/bin/python

#simple flask server for reading dht11 sensor and fetching data

import sys
import subprocess
import time
import Adafruit_DHT
import string

from flask import Flask, render_template, request, redirect
import pytoml as toml

app = Flask(__name__)

DEBUG = False
config = {} #variable to load config form panel_config.toml

#primitive ifconfig parser
def parse_ifconfig(interface):
	retval = []
	
	#try to find hwaddr
	proc_ifconfig = subprocess.Popen(['ifconfig', str(interface)], stdout=subprocess.PIPE)
	#shell=True for trusted input only (shell injection)
	try:
		hwaddr = subprocess.check_output(['grep', 'HWaddr'], stdin=proc_ifconfig.stdout)
	except subprocess.CalledProcessError:
		hwaddr = ''

	proc_ifconfig.stdout.close()
	print hwaddr

	if hwaddr == '' or hwaddr.isspace():
		hwaddr = 'HWaddr:none'
	else:
		hwaddr = 'HWaddr:' + hwaddr.strip().split()[4]

	retval.append(hwaddr)

	#find additional info
	proc_ifconfig = subprocess.Popen(['ifconfig', str(interface)], stdout=subprocess.PIPE)
	try:
		inet_row = subprocess.check_output(['grep', 'inet'], stdin=proc_ifconfig.stdout).strip().split()
	except subprocess.CalledProcessError:
		retval.append("No additioanl info found")
		proc_ifconfig.stdout.close()
		return retval

	proc_ifconfig.stdout.close()

	for i in inet_row[1:]: #skip "inet" in output
		retval.append(i)
	
	return retval

#parsing df output
def parse_df(device):
	#return os.popen('df -h ' + str(device) + ' | tail -n 1', 'r').read().split()
	proc_df = subprocess.Popen(['df', '-h', str(device)], stdout=subprocess.PIPE)
	dev_info = subprocess.check_output(['tail', '-n', '1'], stdin=proc_df.stdout).split()
	proc_df.stdout.close()
	
	return dev_info


@app.route('/')
def hello_world():
	sensor = 11 #config['dht']['sensor_type']
	pin = 13 #config['dht']['pin']
	(hum, temp) = Adafruit_DHT.read_retry(sensor, pin)
	date = subprocess.check_output(['date'])
	uptime = subprocess.check_output("uptime | awk -F, {'print $1$2'}", shell=True)
	uptime = uptime[10:].replace('  ', ' ') #remove date and redundant space
	loadavg = subprocess.check_output(['cat', '/proc/loadavg'])

	interfaces = [] #tuples in format (interface name(string),interface info (list of strings))
	for interface in config['ifconfig']['interfaces']:
		parsed_info = parse_ifconfig(interface)
		interfaces.append((interface, parsed_info))

	devices = []
	for device in config['disks']['devices']:
		parsed_info = parse_df(device)
		devices.append(parsed_info)

	return render_template('index.html', uptime=uptime,
					     config=config,
					     date=date,
					     loadavg=loadavg,
					     interfaces=interfaces,
					     devices=devices,
					     hum=hum,temp=temp)

@app.route('/getTemp')
def get_temp():
	sensor = config['dht']['sensor_type']
	pin = config['dht']['pin']
	(hum, temp) = Adafruit_DHT.read_retry(sensor, pin) 

	if temp is not None and hum is not None:
		return '{"temp" : ' + str(temp) + ',"hum" : ' + str(hum) + '}'

	return '{"temp" : "none" , "hum" : "none"}'

@app.route('/ipconf')
def ipconf():
	return subprocess.check_output(['ifconfig'])

@app.route('/uptime')
def uptime():
	return subprocess.check_output(['uptime'])
@app.route('/df')
def disks():
	return subprocess.check_output(['df', '-h'])

#requires name:some_name in .css file
@app.route('/getTheme')
def get_theme():
	try:
		proc = subprocess.check_output('cat static/style.css | grep name:', shell=True)
	except subprocess.CalledProcessError:
		return 'No name specified'
	
	proc = proc.split(':')
	if len(proc) == 2:
		return proc[1]

	return 'Invalid name format'

#needs one more refresh after successfuly changing theme
#note that themes are changed server side
@app.route('/setTheme')
def set_theme():
	req_theme = request.args.get('themeName', '')
	known_themes = subprocess.check_output(['ls', 'themes'])

	if req_theme == '':
		return 'Key error<br>Use setTheme?themeName=some_theme.css<br>(current theme is: ' + str(get_theme()) + ')<br>Known themes: ' + known_themes
	
	proc = subprocess.call(['cp', 'themes/' + req_theme, 'static/style.css'])
	if proc == 1:
		return 'Theme not found<br>Known themes:' + known_themes

	#return 'Theme changed to: ' + req_theme
	return redirect('/')

if __name__ == '__main__':

	#load config
	with open('panel_config.toml') as config_file:
		config = toml.load(config_file)
	
	app.run(host='raspberrypi.local', debug=DEBUG)

