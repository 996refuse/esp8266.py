import threading
import sys
import serial
import collections
import Queue

class ESP8266:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200):
        self._conn = serial.Serial(port=port, baudrate=baudrate)
        # test
        #self._conn.write('ATE0\r\n')
        #self._conn.write('AT+CIPDINFO=1\r\n')
        
        self._identifiers = collections.deque()
        self._identifiers_top = None
        
        self._recv = ""
        self._reader = threading.Thread(target=self._read, name='reader')
        self._reader.start()
        
        self._on_network_data = lambda: "Network Data Received"
        
        self._results = Queue.Queue()
        
        #self.runCommand()
        
    def _read(self):
        while True:
            data = self._conn.read(self._conn.in_waiting or 1)
            self._recv += data
            #print "@@@", data
            
            if self._recv.startswith('\r\n+IPD'):
                c1 = self._recv.find(',')
                c2 = self._recv[self._recv.find(',')+1:].find(',')
                c3 = self._recv.find(':')
                length = int(self._recv[c1+c2+2:c3])
                network_data = self._recv[:c3+1+length]
                self._recv = self._recv[c3+1+length:]
                self._on_network_data(network_data)

                
            if len(self._identifiers) > 0 and self._identifiers_top == None:
                self._identifiers_top = self._identifiers.popleft()
                
            if self._identifiers_top != None:
                for identifier in self._identifiers_top:
                    index = self._recv.find(identifier)
                    if index != -1:
                        self._identifiers_top = None
                        self._results.put(self._recv[:index + len(identifier)])
                        self._recv = self._recv[index + len(identifier):]
                        break
            
    def onData(self, func):
        self._on_network_data = func
    
    def runCommand(self, command = "ATE0", identifiers = ['OK\r\n', 'ERROR\r\n']):
        self._conn.write(command + '\r\n')
        self._identifiers.append(identifiers)
        
        # try, except flush _identifiers
        return self._results.get(True, 5)
    
    def _restart(self):
        self._recv = ''
        self._identifiers.pop()
        
if __name__ == '__main__':
    esp01 = ESP8266()
    
    @esp01.onData
    def process(data):
        spt = data.find(':')
        print data[:spt]
        print data[spt+1:]
        
    esp01.runCommand('AT+CIPMUX=1')
    esp01.runCommand('AT+CIPSTART=0,"TCP","192.168.199.117",7788', \
                     ["\r\nALREADY CONNECTED\r\n",'\r\nOK\r\n','\r\nERROR\r\n'])
    esp01.runCommand('AT+CIPSTATUS')
    def send(s):
        esp01.runCommand('AT+CIPSEND=0,' + str(len(s)), ['> '])
        esp01.runCommand(s, identifiers=['\r\nSEND OK\r\n'])
    
    send('保存自己消灭敌人这个战争的目的，就是战争的本质\n')
    
    