import yaml
import json
from collections import defaultdict

with open('etc/timeline.json') as tljsonf:
    timeline = json.load(tljsonf)
    # Make sure events are sorted by start date
    for event in timeline['events']:
        if 'month' in event['start_date']:
            event['start_date']['month'] = event['start_date']['month'].rjust(2, '0')
        if 'day' in event['start_date']:
            event['start_date']['month'] = event['start_date']['day'].rjust(2, '0')

    events = timeline['events'].sort(
        key=lambda event: "{0[year]}-{0[month]}-{0[day]}".format(
            defaultdict(str, **(event['start_date']))), reverse=False)
    print(yaml.dump(timeline, default_flow_style=False))
