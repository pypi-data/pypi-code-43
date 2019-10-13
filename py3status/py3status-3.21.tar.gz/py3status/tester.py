import json
from time import sleep
import sys
from syslog import syslog

o = sys.__stdout__

def out(msg):
    o.write(msg + "\n")
    o.flush()

out('{"version":1}')
out('[')

j = {
    "name": "test",
    "instance": "",
    "full_text": "M",
    "short_text": ".",
}

N = 1

out("[" + json.dumps(j) + "]")
while True:
    if len(j["full_text"]) < 137:
        j["full_text"] += "M"
#    syslog("{}".format(len(j["full_text"])))
    out(",[" + json.dumps(j) + "]")
    sleep(0.005)
