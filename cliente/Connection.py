import Pyro5.api


class Connection:
    def __init__(self, uri):
        self.uri = uri

    def server(self):
        return Pyro5.api.Proxy(self.uri)


def server():
    connection = Connection("PYRO:server@18.228.154.72:9090")
    return connection.server()
