#!/usr/bin/env python3

from presidentsCTF import config, notify

config.load_config('prod-config.json')
notify.send_twitter_messages(["mic check...testing...testing...123"])
