import json
import csv
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import defaultdict

env = Environment(
    loader=FileSystemLoader("etc/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

# with open('/Users/jduprey/Source/c3-rdp2/src/assets/org.csv') as orgcsvf:
with open("/Users/jduprey/Downloads/org.csv") as orgcsvf:
    csv_reader = csv.DictReader(orgcsvf, delimiter=",")
    sortedlist = sorted(csv_reader, key=lambda row: (row["name"]), reverse=False)

    anchors = []
    anchor = ""
    for row in sortedlist:
        if anchor != row["name"][0].upper():
            anchor = row["name"][0].upper()
            anchors.append(anchor)

    locations = {}
    for row in sortedlist:
        location = row["location"]
        if location not in locations:
            locations[location] = 0
        locations[location] += 1
        row["bio"] = re.sub("^<span.*Biography</span>", "", row["bio"])
        # row['bio'] = """
        # Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
        # """

    # Generate the HTML from the template
    template = env.get_template("meet-the-team.html")
    print(
        template.render(
            {
                "rows": sortedlist,
                "anchors": anchors,
                "num_locations": len(locations),
                "locations": locations,
            }
        )
    )
