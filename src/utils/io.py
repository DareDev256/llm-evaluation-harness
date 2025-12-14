import json
import yaml
from typing import List, Any, Type
from pydantic import BaseModel

def read_jsonl(path: str, model: Type[BaseModel] = None) -> List[Any]:
    data = []
    with open(path, 'r') as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            if model:
                data.append(model.model_validate(obj))
            else:
                data.append(obj)
    return data

def write_json(data: Any, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def read_yaml(path: str) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)
