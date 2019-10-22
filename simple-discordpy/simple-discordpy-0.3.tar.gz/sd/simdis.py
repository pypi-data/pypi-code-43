import discord
import queue
import asyncio
from threading import Thread

loop = asyncio.get_event_loop()
q = queue.Queue()

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return

        q.put(message.content)

    async def send_msg(self, message):
        for ch in self.get_all_channels():
            if isinstance(ch, discord.TextChannel):
                await ch.send(message)

    async def send_img(self, url):
        import io
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                for ch in self.get_all_channels():
                    if isinstance(ch, discord.TextChannel):
                        await ch.send(file=discord.File(data, 'cool_image.png'))


client = MyClient()

def f(loop, token):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start(token))

def sdinput():
    return q.get()

def sdstart(token):
    Thread(target=f, args=(loop, token)).start()

def sdstop():
    asyncio.run_coroutine_threadsafe(client.close(), loop)

def sdprint(*values):
    asyncio.run_coroutine_threadsafe(client.send_msg(' '.join([str(value) for value in values])), loop).result()

def sdstatus(msg):
    activity = discord.Activity(name=msg, type=discord.ActivityType.playing)
    asyncio.run_coroutine_threadsafe(client.change_presence(activity=activity), loop).result()

def sdimg(url):
    asyncio.run_coroutine_threadsafe(client.send_img(url), loop).result()


