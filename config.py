from json import load
import os

def get_config() -> dict:
    with open(f'{os.path.dirname(os.path.abspath(__file__))}/config.json', 'r') as f:
        config = load(f)
    if not os.path.exists(config['output_location']): os.mkdir(config['output_location'])
    return config
