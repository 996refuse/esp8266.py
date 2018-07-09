import threading
from serial import Serial
import time
import Queue

name = "esp8266.py"
__all__ = ["ESP8266"]

class ESP8266Serial(Serial):
    def __init__(self, *args, **kwargs):
        super(ESP8266Serial, self).__init__(*args, **kwargs)
        self.hw_reset()

        self._identifier_msg_lock = threading.Lock()
        self._identifier_msg = {}

        self._identifier_at_lock = threading.Lock()
        self._identifier_at = []

        self._reader_buffer = ''
        self._reader_thread = threading.Thread(target=self._reader, name='_reader')
        self._reader_thread.start()

    def _reader(self):
        while True:
            c = self.read(1)
            self._reader_buffer += c

            with self._identifier_msg_lock:
                if self._reader_buffer in self._identifier_msg:
                    func = self._identifier_msg[self._reader_buffer]
                    func(self._reader_buffer)
                    self._reader_buffer = ''

            with self._identifier_at_lock:
                if self._identifier_at:
                    for tail in self._identifier_at[0]:
                      if self._reader_buffer.endswith(tail):
                            at = self._identifier_at.pop(0)
                            func = at[tail]
                            func(self._reader_buffer, tail)
                            self._reader_buffer = ''
                            break

    def hw_reset(self):
        print 'reset ...'

        self.write('AT+RST\r\n')
        time.sleep(2)

        # disable echo
        self.write('ATE0\r\n')
        time.sleep(0.5)

        # enable SoftAP mode
        self.write('AT+CWMODE_CUR=2\r\n')
        time.sleep(0.5)

        # config SoftAP
        self.write('AT+CWSAP_CUR="esp8266.py","11111111",5,3\r\n')
        time.sleep(0.5)

        # set server port 8080
        self.write('AT+CIPMUX=1\r\n')
        time.sleep(0.5)
        self.write('AT+CIPSERVER=1,8080\r\n')
        time.sleep(0.5)
        self.reset_input_buffer()
        self._reader_buffer = ''

    def msg_protocol(self, head, func):
        with self._identifier_msg_lock:
            self._identifier_msg[head] = func

    def at_command(self, command, tail_callback_map):
        with self._identifier_at_lock:
            self._identifier_at.append(tail_callback_map)
            self.write(command)

    def __exit__(self, *args, **kwargs):
        self._reader_thread.join(1)
        super(ESP8266Serial, self).__exit__(*args, **kwargs)


class ESP8266(ESP8266Serial):
    def __init__(self, *args, **kwargs):
        Serial.__init__(self)
        super(ESP8266, self).__init__(*args, **kwargs)

        self._send_res = Queue.Queue()
        self._on_data_callback = lambda d, l: None

        msg_config = {
            '0,CONNECT\r\n' : self._echo,
            '1,CONNECT\r\n' : self._echo,
            '2,CONNECT\r\n' : self._echo,
            '3,CONNECT\r\n' : self._echo,
            '0,CLOSED\r\n'  : self._echo,
            '1,CLOSED\r\n'  : self._echo,
            '2,CLOSED\r\n'  : self._echo,
            '3,CLOSED\r\n'  : self._echo,
            '\r\n+IPD,'     : self._ipd
        }

        for k in msg_config:
            self.msg_protocol(k, msg_config[k])

    def _echo(self, buf, tail=None):
        self._callback_result = buf
        print buf

    def _ipd(self, x):
        link_id = ''
        while True:
            tmp = self.read(1)
            if tmp == ',':
                break
            link_id += tmp

        data_length = ''
        while True:
            tmp = self.read(1)
            if tmp == ':':
                break
            data_length += tmp

        length = int(data_length)
        data = self.read(length)

        new_thread = threading.Thread(target=self._on_data_callback, args=(data, link_id))
        new_thread.start()

    def on_data(self, func):
        self._on_data_callback = func

    def send(self, data, link_id):
        def callback(buf, tail):
            print buf
            self._send_res.put(tail)

        _AT_SENT = {'OK\r\n> ': callback, 'ERROR\r\n': callback}
        _AT_SENT_DATA = {'SEND OK\r\n': self._echo, 'SEND FAIL\r\n': self._echo}

        self.at_command('AT+CIPSEND=' + link_id + ',' + str(len(data)) + '\r\n', _AT_SENT)
        res = self._send_res.get()
        if res == 'OK\r\n> ':
            self.at_command(data, _AT_SENT_DATA)

if __name__ == '__main__':
    #from esp8266 import ESP8266
    import sys

    esp01 = ESP8266(port="/dev/ttyAMA0", baudrate=115200)

    esp01.at_command('AT\r\n',{
        'OK\r\n': lambda b,t: sys.stdout.write("1\n"),
        'ERROR\r\n': lambda b,t: sys.stdout.write("0\n")
    })

    @esp01.on_data
    def on_data(data, link_id):
        print '@@@@@@ data arrived:'
        print 'link id:', link_id
        print data
        esp01.send("Hello, world! \n", '0')

