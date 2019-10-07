
import zmq
import time
import threading

print(f"zmq_version {zmq.zmq_version()}")

channel = "ipc://routing.ipc"

channel_conn = "tcp://localhost:5555"
channel_bind = "tcp://*:5555"


def task_dealer(identity: bytes):
    flask_context = zmq.Context().instance()
    socket_dealer = flask_context.socket(zmq.DEALER)
    socket_dealer.setsockopt(zmq.PROBE_ROUTER, 1)

#     socket_dealer.setsockopt(zmq.IDENTITY, b'0x00')
#     socket_dealer.setsockopt(zmq.IDENTITY, identity)
    socket_dealer.connect(channel_conn)
    time.sleep(1)

    while True:
#         request = socket_dealer.recv()
#         print(f"request: {request}")
        source = b'hello'
        socket_dealer.send_multipart([source, identity, ])
        time.sleep(2)


dealer_1 = threading.Thread(target=task_dealer, args=[b'A'])
dealer_1 .start()

dealer_2 = threading.Thread(target=task_dealer, args=[b'B'])
dealer_2 .start()

flask_context = zmq.Context.instance()
socket_router = flask_context.socket(zmq.ROUTER)
socket_router.setsockopt(zmq.PROBE_ROUTER, 1)

socket_router.bind(channel_bind)

while True:
#     socket_router.send_multipart([b'A', b'hello'])
#     time.sleep(1)
#     socket_router.send_multipart([b'B', b'world'])
#     time.sleep(1)
    request = socket_router.recv_multipart()
    print(f"id: {request[0]} source: {request[1:]}")
    response = request
    socket_router.send_multipart(response)
