import YHDDsocket

__all__ = ["TCPServer","BaseRequestHandler",
           "StreamRequestHandler"]

class TCPServer:
    def __init__(self, server_address, RequestHandlerClass):
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass

        self.socket = YHDDsocket.socket()

        try:
            self.server_bind()
        except:
            self.server_close()
            raise

    def serve_forever(self):
        while True:
            self._handle_request_noblock()

    def _handle_request_noblock(self):
        request, client_address = self.get_request()
        try:
            self.process_request(request, client_address)
        except:
            self.handle_error(request, client_address)
            request.close()

    def process_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self)
        request.close()

    def server_bind(self):
        pass

    def server_close(self):
        self.socket.close()

    def get_request(self):
        return self.socket.accept()

    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.

        The default is to print a traceback and continue.

        """
        print '-'*40
        print 'Exception happened during processing of request from',
        print client_address
        import traceback
        traceback.print_exc() # XXX But this goes to stderr!
        print '-'*40


class BaseRequestHandler:
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()
    def setup(self):
        pass

    def handle(self):
        pass

    def finish(self):
        pass


class StreamRequestHandler(BaseRequestHandler):
    def setup(self):
        self.connection = self.request
        self.rfile = self.connection.makefile()
        self.wfile = self.connection.makefile()

    def finish(self):
        '''
        if not self.wfile.closed:
            try:
                self.wfile.flush()
            except socket.error:
                # An final socket error may have occurred here, such as
                # the local error ECONNABORTED.
                pass
        '''
        self.wfile.close()
        self.rfile.close()

