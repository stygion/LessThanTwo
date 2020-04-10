import json
import os
from shutil import copyfile

CONFIG_PATH = 'config/config.json'
DEFAULT_CONFIG_PATH = 'config/default_config.json'

config = None

def get(key):
    if not config:
        _load_config()
    return config.get(key)
        
def _load_config():
    if not os.path.isfile(CONFIG_PATH):
        copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)

    global config
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
