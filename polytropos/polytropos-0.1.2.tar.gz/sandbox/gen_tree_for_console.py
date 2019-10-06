"""Create a sample of an easy-to-use format for the console. We will write a converter from this format later."""
import json
from collections import OrderedDict
from typing import List, Dict

from polytropos.ontology.schema import Schema
from faker import Faker
import random

schemas_dir: str = "/dmz/github/analysis/polytropos/examples/s_7_csv/conf/schemas"
schema: Schema = Schema.load("composite", schemas_dir)

tree: List[Dict] = []
fake: Faker = Faker('en_US')

def add_fake_metadata_to(subtree: Dict) -> None:
    n_metadata_items: int = 1
    metadata: OrderedDict = OrderedDict()
    for i in range(5):
        n_metadata_items += random.randint(0, 2)

    for i in range(n_metadata_items):
        key = " ".join(fake.words(nb=random.randint(1, 3)))
        value = fake.paragraph()
        metadata[key] = value
    subtree["metadata"] = metadata

def add_fake_sources_to(subtree: Dict) -> None:
    n_sources: int = random.randint(1, 5)
    var_id: str = subtree["varId"]
    sources: List = []
    for i in range(1, n_sources + 1):
        sources.append("source_%i_for_%s" % (i, var_id))
    subtree["sources"] = sources

def add_fakes_to(subtree: Dict) -> None:
    if bool(random.getrandbits(1)):
        add_fake_metadata_to(subtree)
    if bool(random.getrandbits(1)) and not subtree["dataType"] == "Folder":
        add_fake_sources_to(subtree)
    if "children" in subtree:
        for child in subtree["children"]:
            add_fakes_to(child)

for root in schema.immutable.roots:
    subtree: Dict = root.tree
    add_fakes_to(subtree)
    tree.append(root.tree)

with open("/dmz/output/sample.json", "w") as fh:
    json.dump(tree, fh, indent=2)
