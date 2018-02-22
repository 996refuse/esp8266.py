import threading
from serial import Serial
import time
import Queue

class ESP8266Serial(Serial):
    def __init__(self, *args, **kwargs):
        Serial.__init__(self)
        super(ESP8266Serial, self).__init__(*args, **kwargs)
        self.hw_reset()

        self._identifier_msg_lock = threading.Lock()
        self._identifier_msg = {}

        self._identifier_at_lock = threading.Lock()
        self._identifier_at = []

        self._reader_buffer = ''
        self._readerThread = threading.Thread(target=self._reader, name='_reader')
        self._readerThread.start()

    def _reader(self):
        while True:
            c = self.read(1)
            self._reader_buffer += c

            with self._identifier_msg_lock:
                if self._reader_buffer in self._identifier_msg:
                    _reader_buffer = self._reader_buffer
                    self._reader_buffer = ''

                    func = self._identifier_msg[_reader_buffer]
                    func(_reader_buffer)

            with self._identifier_at_lock:
                if self._identifier_at:
                    for tail in self._identifier_at[0]:
                        if self._reader_buffer.endswith(tail):
                            _reader_buffer = self._reader_buffer
                            self._reader_buffer = ''

                            at = self._identifier_at.pop(0)
                            func = at[tail]
                            func( _reader_buffer, tail)

                            break

    def hw_reset(self):
        print 'reset ...'

        self.write('AT+RST\r\n')
        time.sleep(1)

        # disable echo
        self.write('ATE0\r\n')
        time.sleep(0.2)

        # enable SoftAP mode
        self.write('AT+CWMODE_CUR=2\r\n')
        time.sleep(0.2)

        # config SoftAP
        self.write('AT+CWSAP_CUR="esp8266py","88888888",5,3\r\n')
        time.sleep(0.2)

        # set server port 8080
        self.write('AT+CIPMUX=1\r\n')
        time.sleep(0.2)
        self.write('AT+CIPSERVER=1,8080\r\n')
        time.sleep(0.2)
        self.reset_input_buffer()
        self._reader_buffer = ''

    def add_msg_protocol(self, head, func):
        with self._identifier_msg_lock:
            self._identifier_msg[head] = func

    def run_at_command(self, command, tail_callback_map):
        with self._identifier_at_lock:
            self._identifier_at.append(tail_callback_map)
        self.write(command)

    def __del__(self):
        self._readerThread.join(1)

result = None
def echo(buf, tail=None):
    global result
    result = buf
    print buf

class ESP8266(ESP8266Serial):
    def __init__(self, *args, **kwargs):
        Serial.__init__(self)
        super(ESP8266, self).__init__(*args, **kwargs)

        self._send_res = Queue.Queue()

        self._onData = lambda d, l: None

        def _ipd(x):
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
            self._onData(data, link_id)

        msg_config = {
            '0,CONNECT\r\n' : echo,
            '1,CONNECT\r\n' : echo,
            '2,CONNECT\r\n' : echo,
            '3,CONNECT\r\n' : echo,
            '0,CLOSED\r\n'  : echo,
            '1,CLOSED\r\n'  : echo,
            '2,CLOSED\r\n'  : echo,
            '3,CLOSED\r\n'  : echo,
            '\r\n+IPD,'     : _ipd
        }

        for k in msg_config:
            self.add_msg_protocol(k, msg_config[k])

    def on_data(self, func):
        self._onData = func

    def send(self, data, link_id):
        new_thread = threading.Thread(target=self._send, name='_send', args=(data, link_id))
        new_thread.start()

    def _send(self, data, link_id):
        def callback(buf, tail):
            print buf
            self._send_res.put(tail)

        _AT_SENT = {'OK\r\n> ': callback, 'ERROR\r\n': callback}
        _AT_SENT_DATA = {'SEND OK\r\n': echo, 'SEND FAIL\r\n': echo}

        self.run_at_command('AT+CIPSEND=' + link_id + ',' + str(len(data)) + '\r\n', _AT_SENT)

        res = self._send_res.get()
        if res == 'OK\r\n> ':
            self.run_at_command(data, _AT_SENT_DATA)

if __name__ == '__main__':
    esp01 = ESP8266(port="/dev/ttyAMA0", baudrate=115200)

    @esp01.on_data
    def on_data(data, link_id):
        print '@@@@@@ data arrived:'
        print 'link id:', link_id
        print data
        esp01.send("hello world \n", link_id)