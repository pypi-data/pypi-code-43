from aioitertools import iter


class Subscriber:
    def __init__(self, method):
        self.method = method

    async def on_response(self, **kwargs):
        await self.method(kwargs)


class Publisher:
    def __init__(self):
        self.subscriber_list = []

    def register(self, subscriber):
        if not self.subscriber_list.__contains__(subscriber):
            self.subscriber_list.append(subscriber)

    def unregister(self, subscriber):
        if not self.subscriber_list.__contains__(subscriber):
            self.subscriber_list.remove(subscriber)

    async def invoke(self, **kwargs):
        async for sub in iter(self.subscriber_list):
            await sub.on_response(kwargs)
