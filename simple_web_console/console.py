import json

from tornado import websocket, web, ioloop

from common.cmd import run_cmd
from libs.ansi2html import Ansi2HTMLConverter

clients = []

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        print('check origin adress:' + str(origin))
        return True

    def open(self):
        print('open connection to client:' + str(clients))
        if self not in clients:
            clients.append(self)

    def on_close(self):
        if self in clients:
            clients.remove(self)

class ApiHandler(web.RequestHandler):

    
    def handle(self, *args):
        conv = Ansi2HTMLConverter()
        try:
            print('get:' + str(args))
            self.finish()
            cmd = self.get_argument("cmd")
            id = self.get_argument("id")

            out = run_cmd(cmd)
            print(out)
            ansi = "".join(out)
            #sys.stdin.readlines()
            html = conv.convert(ansi)

            data = {"id": id, "value" : html}

            print('send message to all {} clients', len(clients));
            data = json.dumps(data)
            for c in clients:
                c.write_message(data)
        except Exception as e:
            print(str(e))
            data = {"id": id, "value" : conv.convert("".join((R,str(e),W)))}
            for c in clients:
                c.write_message(data)

    @web.asynchronous
    def get(self, *args):
        self.handle(self,args)

    @web.asynchronous
    def post(self,*args):
        self.handle(self,args)

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    #(r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    #(r'/(js/jquery-3.1.1.min.js)', web.StaticFileHandler, {'path': './'}),
    #(r'/(css/bootstrap.min.css)', web.StaticFileHandler, {'path': './'}),
    (r"/(.*)", web.StaticFileHandler, {"path": "./static"}),
])

if __name__ == '__main__':
    app.listen(9988)
    ioloop.IOLoop.instance().start()
