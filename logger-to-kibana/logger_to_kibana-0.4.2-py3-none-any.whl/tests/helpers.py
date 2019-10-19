import os
import json


def get_test_results_json_file(name: str) -> dict:
    with open(os.path.abspath(f"tests/unit/resources/" + name)) as file:
        return json.loads(file.read())
