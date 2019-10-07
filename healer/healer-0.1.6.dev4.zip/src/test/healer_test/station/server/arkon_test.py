
import time

from healer.station.server.arkon import *


def test_server_server():
    print()

    app = FlaskBuilder.produce_app(config.TestConfig)

    server = FlaskServer(app)

    server.start()

    time.sleep(1)

    server.stop()
