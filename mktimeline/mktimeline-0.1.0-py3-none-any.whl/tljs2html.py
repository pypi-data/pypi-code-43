import json
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import defaultdict

env = Environment(
    loader=FileSystemLoader('etc/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

with open('etc/timeline.json') as tljsonf:
    timeline = json.load(tljsonf)

    # Fix title media
    if timeline['title']['media']['url'].find('//youtu') != -1:
        timeline['title']['media']['url'] = re.sub(
            r".*\/(.*)$", r'https://youtube.com/embed/\1?rel=0', timeline['title']['media']['url'])

    # Make sure events are sorted by start date
    events = timeline['events'].sort(
        key=lambda event: "{0[year]}-{0[month]}-{0[day]}".format(
            defaultdict(str, **(event['start_date']))), reverse=False)

    # Convert media youtube URLs to embed urls...
    for event in timeline['events']:
        if 'media' in event and 'url' in event['media'] and event['media']['url'].find('//youtu') != -1:
            event['media']['url'] = re.sub(
                r".*\/(.*)$", r'https://youtube.com/embed/\1?rel=0', event['media']['url'])

    # Generate the HTML from the template
    template = env.get_template('non-interactive.html')
    print(template.render(timeline))
