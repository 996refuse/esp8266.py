import threading
import sys
import serial
import collections

class ESP8266:
    def __init__(self):
        
        self._conn = serial.Serial(port="/dev/ttyUSB0", baudrate=115200)
        self._recv = ""
        self._identifiers = collections.deque()
        
        self._reader = threading.Thread(target=self._read, name='reader')
        self._reader.start()
        
        self._on_network_data = lambda data: "Network Data Received"
        
        self._result = None
        self._result_lock = threading.Lock()
        self._result_lock.acquire()
        
    def _read(self):
        while True:
            data = self._conn.read(self._conn.in_waiting or 1)
            self._recv += data
            
            sys.stdout.write(data)
            
            if self._recv.startswith('+IPD'):
                try:
                    c1 = s.find(',')
                    c2 = s[s.find(',')+1:].find(',')
                    c3 = s.find(':')
                    length = int(s[c1+c2+2:c3])
                    network_data = s[:c3+1+length]
                    self._recv = self._recv[c3+1+length:]
                    self._on_network_data(network_data)
                except:
                    pass
                
            for identifiers in self._identifiers:
                for identifier in identifiers:
                    index = self._recv.find(identifier)
                    if index != -1:
                        self._result = self._recv[:index + len(identifier)+2]
                        self._recv = self._recv[index + len(identifier)+2:]
                        self._result_lock.release()
                        break
            
    def onData(self, func):
        self._on_network_data = func
    
    def runCommand(self, command = "ATE0", identifiers = ["OK"]):
        self._conn.write(command + '\r\n')
        self._identifiers.append(identifiers)
        self._result_lock.acquire()
        return self._result
        