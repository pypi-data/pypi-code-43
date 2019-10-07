
import zmq
import time
import threading
from alembic.util.compat import reraise

print(f"zmq_version {zmq.zmq_version()}")

channel_conn = "tcp://localhost:5555"
channel_bind = "tcp://*:5555"

flask_context = zmq.Context.instance()
socket_router = flask_context.socket(zmq.ROUTER)

while True:
    print(f"bind")

    try:
        socket_router.bind(channel_bind)
    except zmq.error.ZMQError as error:
        if error.errno == zmq.EADDRINUSE:
            print(f"error: EADDRINUSE")
        else:
            print(f"error: {error.errno}")
            reraise

    time.sleep(1)
