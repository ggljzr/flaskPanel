# flaskPanel
Simple web panel for displaying sensor values on raspberry pi using flask framework (http://flask.pocoo.org/). Panel can be configured via panel_config.toml file. Server is running on port 5000 (default raspberrypi.local:5000)

Sensor is DHT11 and it is read with Adafruit DHT library (https://github.com/adafruit/Adafruit_Python_DHT).

To run use "sudo python flaskPanel.py" (sudo is needed for access to Rpi's GPIO pins).

##dependencies
You need Flask, pytoml and Adafruit DHT library. 
On Raspberry Pi Flask can be installed with package manager 
<pre><code>
sudo apt-get install python-flask
</code></pre>

Pytoml can be installed with pip package manager
<pre><code>
sudo pip install pytoml
</code></pre>
You may have to install pip with standard package manager first.

For installing Adafruit DHT library follow the link above.

![Alt text](pic.png?raw=true "Flask Panel")
