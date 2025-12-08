# app/config_manager.py
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_CONFIG = {
    "total_leds": 70,
    "letters": {
        "P": [0, 6],
        "H": [7, 13],
        "O": [14, 20],
        "N": [21, 27],
        "E": [28, 34],
        "A": [35, 41],
        "I": [42, 48],
        "D": [49, 55]
    },
    "standby": {
        "start": "21:00",
        "end": "08:00"
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
