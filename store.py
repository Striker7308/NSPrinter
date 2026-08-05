import json

def load_store_config(config_file="./config/store.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)
