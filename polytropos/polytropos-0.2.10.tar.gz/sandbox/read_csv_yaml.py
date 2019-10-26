import yaml
import json

with open("/mnt/dmz/github/analysis/polytropos/examples/s_7_csv/conf/tasks/05_temporal_list_and_immutable_keyed_list.yaml") as fh:
    contents = yaml.full_load(fh)
    print(json.dumps(contents, indent=2))
