from mwrpc import MwrServer

server = MwrServer()


@server.func(endpoint='calc')
def add(a, b):
    return a + b


@server.func(endpoint='test')
def test():
    return "Hello World"


if __name__ == '__main__':
    server.run()
