from esp8266 import ESP8266
import sys
import Queue


class _socketobject(object):
    def __init__(self):
        self.esp01 = ESP8266(port="/dev/ttyAMA0", baudrate=115200)
        self.esp01.at_command('AT\r\n', {
            'OK\r\n': lambda b, t: sys.stdout.write("1\n"),
            'ERROR\r\n': lambda b, t: sys.stdout.write("0\n")
        })

        self.readbuf = []
        for i in range(4):
            self.readbuf.append( Queue.Queue() )

        @self.esp01.on_data
        def on_data(data, link_id):
            self.readbuf[int(link_id)].put(data)
            #esp01.send("Hello, world! \n", '0')

        messages = [
            '0,CONNECT\r\n',
            '1,CONNECT\r\n',
            '2,CONNECT\r\n',
            '3,CONNECT\r\n'
        ]

        self.link_id = None
        self.msg_queue = Queue.Queue()
        for msg in messages:
            self.esp01.msg_protocol(msg, self.add_queue)



    def add_queue(self, buf, tail=None):
        self.msg_queue.put(buf[0])
        sys.stdout.write("add_queue ok "+buf[0]+"\n")

    def close(self):

        if self.link_id is not None:
            self.esp01.at_command('AT+CIPCLOSE='+self.link_id+'\r\n', {
                'OK\r\n': lambda b, t: sys.stdout.write("close ok 1\n"),
                'ERROR\r\n': lambda b, t: sys.stdout.write("close error 0\n")
            })
        self.link_id = None


    def accept(self):
        self.link_id = self.msg_queue.get()
        return self, self.link_id

    def makefile(self):
        return _fileobject(sock=self)


socket = SocketType = _socketobject

class _fileobject(object):
    def __init__(self, sock):
        self.link_id = sock.link_id
        self.sock = sock

    def close(self):
        sys.stdout.write("file close " + self.link_id + "\n")
        pass

    def write(self, data):
        self.sock.esp01.send(data, self.link_id)

    def readline(self, size=-1):
        buf = self.sock.readbuf[int(self.link_id)]
        res = ""
        while buf.qsize() > 0:
            res += buf.get_nowait()
        return res
