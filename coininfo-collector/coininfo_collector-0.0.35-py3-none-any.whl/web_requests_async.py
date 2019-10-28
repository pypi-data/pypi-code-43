# -*- coding: utf-8 -*-
import aiohttp

async def async_get(log, url, headers=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                text = await resp.text()
                if resp.status is not 200:
                    log.error('GET {} failed with status {} - {}'.format(url, resp.status, text))
                    return None
                return await resp.json()
    except Exception as inst:
        log.error('exception in fetch. url:{} msg:{}'.format(url, inst.args))
        return None