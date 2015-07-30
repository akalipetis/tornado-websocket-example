import json

from datetime import timedelta
from tornado import websocket, web, ioloop


cl = []


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument('id')
        value = self.get_argument('value')
        data = {'id': id, 'value' : value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        pass

app = web.Application([
        (r'/', IndexHandler),
        (r'/ws', SocketHandler),
        (r'/api', ApiHandler),
        (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
        (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
    ], debug=True, )


def ping_clients():
    try:
        for client in cl:
            client.ping('ping')
    finally:
        ioloop.IOLoop.instance().add_timeout(
            timedelta(seconds=10), ping_clients
        )


if __name__ == '__main__':
    ioloop.IOLoop.instance().add_timeout(
        timedelta(seconds=10), ping_clients
    )
    app.listen(5000)
    ioloop.IOLoop.instance().start()
