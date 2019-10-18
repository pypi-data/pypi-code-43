#!/usr/bin/env python3

from presidentsCTF import config, notify

config.load_config('prod-config.json')
notify.send_slack_messages(["testing", "123"])
