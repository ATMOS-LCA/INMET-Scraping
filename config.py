from json import load
import subprocess
import os

def get_config() -> dict:
    actualPath = subprocess.run("pwd", stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8").replace('\n', '')
    with open(f'{actualPath}/config.json', 'r') as f:
        config = load(f)
    if not os.path.exists(config['output_location']): os.mkdir(config['output_location'])
    return config
