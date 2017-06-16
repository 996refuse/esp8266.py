# esp8266py
ESP8266 python library, a wrapper for AT commands (Hayes command set) UART serial.
Running on PC/raspberry pi 

# Features

***To use this library, you need to upgrade to the lastest 2.1.0 sdk***
```python
# initial module
from esp8266 import ESP8266
esp01 = ESP8266()

# execute synchronously
res = esp01.runCommand(command="AT")

# callback on data receive
@esp01.onData
def process(data):
    print data

esp01.runCommand('AT+CIPSTART=0,"TCP","192.168.199.117",7788', ['OK', 'ERROR', 'ALREADY CONNECT'])
# then in the host 192.168.199.117, type 'nc -l 7788' in console. you can communicate with each other
# through the module. 
```

# TODO

* turn all at command to function
* route network
