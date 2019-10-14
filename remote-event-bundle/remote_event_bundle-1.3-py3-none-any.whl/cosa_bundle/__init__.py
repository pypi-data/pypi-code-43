from applauncher.kernel import KernelReadyEvent, EventManager
import inject
from remote_event_bundle import RemoteEvent


class MyEvent(RemoteEvent):
    event_name = "my_event"

    def __init__(self, payload):
        self.payload = payload

class ExampleBundle(object):

    def __init__(self):
        self.event_listeners = [
            (KernelReadyEvent, self.kernel_ready),
            (MyEvent, self.new_event)
        ]

    def new_event(self, event):
        print(f"NEW EVENT {event.payload}")

    def kernel_ready(self, event):
        em = inject.instance(EventManager)  #  type: EventManager
        em.dispatch(MyEvent("This is the payload"))
