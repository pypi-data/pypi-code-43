from collections import namedtuple

from marshmallow import Schema, fields

Repo = namedtuple("Repo", ["url", "stars", "description"])
r = Repo('href', 23, 'asdas')
l = Repo('href', 22, 'asdas')
print(r)
ll = [r, l]

import json

print(json.dumps([i._asdict() for i in ll]))
print(json.dumps(r._asdict()))
# row = fields.Tuple((fields.String(), fields.Integer(), fields.String()))
# PersonSchema = Schema.from_dict({"url": fields.Str(), "stars": fields.Integer(), "description": fields.String()})
# print(PersonSchema().load(r))  # => {'name': 'David