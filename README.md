# esp8266.py

ESP8266 python library, a wrapper for AT commands (Hayes command set) using UART serial.
Could be running on PC/raspberry pi easily.

# Dependency

* python2.7
* pySerial

# Hardware wiring (Connect ESP8266-01 to RPI)

    RX    -> TX      VCC   -> 3.3v
    GPIO0            RST
    GPIO2            CH_PD -> 3.3v
    GND   -> ground  TX    -> RX

# Usage

```python
# initialize
# After initialization you could use the default password '11111111' to connect
# to wifi 'esp8266.py' and connect port 8080 on 192.168.4.1 through telnet/nc.
from esp8266 import ESP8266
esp01 = ESP8266(port="/dev/ttyAMA0", baudrate=115200)


# response on data receiving
@esp01.on_data
def on_data(data, link_id):
    print '@@@@@@ data arrived:'
    print 'link id:', link_id
    print data
    esp01.send("pong! \n", link_id)


# send data
esp01.send("hello world \n", '0')
```

# TODO

* WSGI api
