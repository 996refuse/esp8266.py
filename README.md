# esp8266.py
ESP8266 python library, a wrapper for AT commands (Hayes command set) using UART serial.
Could be running on PC/raspberry pi easily.

# Dependency

* python2.7
* pySerial

# Hardware wiring (Connect ESP8266 to RPI)

# Usage

```python
# initialize
from esp8266 import ESP8266
esp01 = ESP8266(port="/dev/ttyAMA0", baudrate=115200)


# response on data receiving
@esp01.on_data
def on_data(data, link_id):
    print '@@@@@@ data arrived:'
    print 'link id:', link_id
    print data


# send data
esp01.send("hello world \n", link_id)
```

# API

# TODO

* WSGI api
* sync command



