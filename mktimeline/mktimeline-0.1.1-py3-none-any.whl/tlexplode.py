import json
import os.path
import re
from collections import defaultdict
from os import makedirs

import yaml

with open('etc/timeline.json') as tljsonf:
    timeline = json.load(tljsonf)
    title = timeline['title']
    title_text = title.pop('text')

    # Write the Title Markdown File
    yaml_text = "---\n"
    yaml_text += yaml.dump(title, default_flow_style=False)
    yaml_text += "---\n\n"
    yaml_text += "# {} \n\n {}".format(title_text['headline'], title_text['text'])

    filename = "title.md"
    filelocation = os.path.join('etc/timeline', filename)

    with open(filelocation, 'w') as yf:
        yf.write(yaml_text)

    for event in timeline['events']:
        # Write the Title Markdown File
        event_text = event.pop('text')
        yaml_text = "---\n"
        media = event
        yaml_text += yaml.dump(media, default_flow_style=False)
        yaml_text += "---\n\n"
        yaml_text += "# {} \n\n {}".format(
            event_text['headline'], event_text['text'])

        date_prefix = "{0[year]}-{0[month]}-{0[day]}".format(
            defaultdict(str, **(event['start_date'])))
        filename_base = "{}_{}".format(date_prefix, re.sub(
            r'\W+', '_', event_text['headline'].lower()))
        filedir = os.path.join('etc/timeline/events/', filename_base)
        makedirs(filedir, exist_ok=True)
        makedirs(os.path.join(filedir, 'assets'), exist_ok=True)
        filelocation = os.path.join(filedir, "{}.md".format(filename_base))
        with open(filelocation, 'w') as yf:
            yf.write(yaml_text)
