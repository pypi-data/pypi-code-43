import json
from pathlib import Path
from collections import defaultdict

from bin.mdevent2json import to_event

title = to_event('etc/timeline/title.md')

events = []
for filename in Path('etc/timeline/events').glob('**/*.md'):
    event = to_event(filename)
    if event:
        events.append(event)

for event in events:
    if 'month' in event['start_date']:
        event['start_date']['month'] = event['start_date']['month'].rjust(2, '0')
    if 'day' in event['start_date']:
        event['start_date']['month'] = event['start_date']['day'].rjust(2, '0')

# Make sure events are sorted by start date
events.sort(
    key=lambda event: "{0[year]}-{0[month]}-{0[day]}".format(
        defaultdict(str, **(event['start_date']))), reverse=False)

timeline = {'title': title, 'events': events}
print(json.dumps(timeline, indent=4))
