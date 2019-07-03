import json
import os.path
from typing import Any

def load_test_data(filename: str) -> str:
    base_path = os.path.dirname(__file__)
    data_path = os.path.join(base_path, 'test_data', filename)

    with open(data_path, 'r') as data_file:
        return data_file.read()

def load_test_json(filename: str) -> Any:
    return json.loads(load_test_data(filename))
