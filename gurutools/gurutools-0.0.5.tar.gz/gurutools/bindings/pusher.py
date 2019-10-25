from celery import shared_task
from .settings import PUSHER_QUEUE

@shared_task(name='pusher.push_to_pubnub')
def push_to_pubnub(channel, message):
    """

### Example usage:

```
from gurutools.bindings.pusher import delegate_push

delegate_push(
    method = "push_to_pubnub",
    args = (channel, content),
    version = "1"
```
    """
    pass

PUSH_MAP = {
    "1": {
        "push_to_pubnub": push_to_pubnub
    }
}

def delegate_push(method_name, args, version = "1"):
    method_to_call = PUSH_MAP.get(version).get(method_name)
    return method_to_call.apply_async(
        args,
        queue=PUSHER_QUEUE,
        serializer='json'
    )

