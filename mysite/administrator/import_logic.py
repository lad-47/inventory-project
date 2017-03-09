import json

def create_item_from_json(json_item):
    item = json.loads(json_item)
    return item
