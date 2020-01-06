from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
import os
import threading

filename=""

class MyHandler(FTPHandler):
    def on_file_received(self, file):
        print("In handler : ",file)
        global filename
        filename=file.split("/")[-1]

class ftp_server:
    def __init__(self):
        authorizer = DummyAuthorizer()
        authorizer.add_user('user', '12345', 'collected/', perm='elradfmwMT')
        authorizer.add_anonymous("collected/",perm='elradfmwMT')
        self.handler = MyHandler
        self.handler.authorizer = authorizer
        self.obj=ThreadedFTPServer(("0.0.0.0",21), self.handler)
        self.filename=""
        # set a limit for connections
        #self.max_cons = 256
        #self.max_cons_per_ip = 5


    def get_filename(self):
        global filename
        return filename
    
    def _run_server(self):
        self.obj.serve_forever()

    def start(self):
        srv = threading.Thread(target=self._run_server)
        srv.deamon = True
        srv.start()

    def stop(self):
        self.obj.close_all()
