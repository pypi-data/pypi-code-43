#!/usr/bin/env python3

import asyncio
import aiohttp
from aiosmtplib import SMTP, send
import atoma
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

from . import render
from . import config


async def fetch(session, url):
    async with session.get(url) as res:
        return await res.read()


def get_new_items(entries, last_update):
    return [x for x in entries if x.updated > last_update]


async def get_feed_updates(feed, last_update=None):
    async with aiohttp.ClientSession() as s:
        print(f"Fetching updates for {feed}")

        ret = {"name": feed, "new_items": []}

        try:
            body = await fetch(s, feed.strip())
            atom_feed = atoma.parse_atom_bytes(body)
            ret["new_items"] = get_new_items(atom_feed.entries, last_update)
        except Exception as e:
            print(f"Error with {feed}: {e}")

        return ret


async def send_email(new_items, conf):
    html = MIMEText(render.as_html(new_items), "html", "utf-8")
    text = MIMEText(render.as_text(new_items), "plain", "utf-8")

    total_updates = sum([len(x) for x in new_items.values()])
    feeds_updated = len(new_items.keys())

    pluralize = lambda word, count: word if count == 1 else f"{word}s"

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Feed2Mail <{conf.mail_user}>"
    msg["To"] = conf.mail_to
    msg["Subject"] = " ".join([
        f"{total_updates} {pluralize('update', total_updates)}",
        "in",
        f"{feeds_updated} {pluralize('feed', feeds_updated)}"
    ])
    msg.attach(text)
    msg.attach(html)

    await send(
        message=msg,
        hostname=conf.mail_host,
        username=conf.mail_user,
        password=conf.mail_password,
        start_tls=True
    )


def feeds_with_updates(items):
    return [x for x in items if x['new_items']]


def chunk_items(items, chunk_size=3):
    for i in range(0, len(items), chunk_size):
        yield items[i:i+chunk_size]


async def async_main():
    conf = config.parse_args()
    feeds = config.load_feeds(conf.config_path)

    new_items = {}
    for chunk in chunk_items([(x, y) for x,y in feeds.items()]):
        futures = [
            get_feed_updates(url, last_update)
            for url, last_update
            in chunk
        ]
        futures = await asyncio.gather(*futures)

        for feed in feeds_with_updates(futures):
            new_items[feed['name']] = feed['new_items']

    if conf.print:
        print(render.as_text(new_items))

    if not conf.dry_run and len(new_items.keys()) > 0:
        await send_email(new_items, conf)
        config.save_feeds(conf.config_path, feeds, new_items.keys())


def main():
    asyncio.run(async_main())
