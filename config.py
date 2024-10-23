from json import load
import os

def get_config() -> dict:
    with open('config.json', 'r') as f:
        config = load(f)
    if not os.path.exists(config['output_location']): os.mkdir(config['output_location'])
    return config
