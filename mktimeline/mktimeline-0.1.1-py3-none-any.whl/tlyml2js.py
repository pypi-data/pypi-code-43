import yaml
import json
from collections import defaultdict

with open('etc/timeline.yml') as tlyamlf:
    timeline = yaml.load(tlyamlf)

    for event in timeline['events']:
        if 'month' in event['start_date']:
            event['start_date']['month'] = event['start_date']['month'].rjust(2, '0')
        if 'day' in event['start_date']:
            event['start_date']['month'] = event['start_date']['day'].rjust(2, '0')

    # Make sure events are sorted by start date
    events = timeline['events'].sort(
        key=lambda event: "{0[year]}-{0[month]}-{0[day]}".format(
            defaultdict(str, **(event['start_date']))), reverse=False)
    print(json.dumps(timeline, indent=4))
