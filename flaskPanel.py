#!/usr/bin/python

#simple flask server for reading dht11 sensor and fetching data

import sys
import subprocess
import time
import Adafruit_DHT
import string

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

sensor = 11 #using DHT11 sensor
pin = 13 #connected to pin 13

#primitive ifconfig parser
def parse_ifconfig(interface):
	retval = []
	
	#try to find hwaddr
	proc_ifconfig = subprocess.Popen(['ifconfig', interface], stdout=subprocess.PIPE)
	#shell=True for trusted input only (shell injection)
	hwaddr = subprocess.check_output("grep HWaddr | awk -F' ' '{print $5}'", stdin=proc_ifconfig.stdout, shell=True)
	proc_ifconfig.stdout.close()

	if hwaddr == '' or hwaddr.isspace():
		hwaddr = 'HWaddr:none'
	else:
		hwaddr = 'HWaddr:' + hwaddr.strip()

	retval.append(hwaddr)

	for i in range(2,5):
		proc_ifconfig = subprocess.Popen(['ifconfig', str(interface)], stdout=subprocess.PIPE)
		info = subprocess.check_output("grep inet | awk -F' ' '{print $" + str(i) + "}'", 
						stdin=proc_ifconfig.stdout, shell=True)
		proc_ifconfig.stdout.close()

		if info == '' or info.isspace():
			continue
		else:
			retval.append(info)
	
	return retval

#parsing df output
def parse_df(device):
	#return os.popen('df -h ' + str(device) + ' | tail -n 1', 'r').read().split()
	proc_df = subprocess.Popen(['df', '-h', str(device)], stdout=subprocess.PIPE)
	dev_info = subprocess.check_output(['tail', '-n', '1'], stdin=proc_df.stdout)
	proc_df.stdout.close()
	return dev_info.split()


@app.route('/')
def hello_world():
	(hum, temp) = Adafruit_DHT.read_retry(sensor, pin)
	date = subprocess.check_output(['date'])
	uptime = subprocess.check_output("uptime | awk -F, {'print $1$2'}", shell=True)
	uptime = uptime[10:].replace('  ', ' ') #remove date and redundant space
	loadavg = subprocess.check_output(['cat', '/proc/loadavg'])

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
	app.run(host='raspberrypi.local')

