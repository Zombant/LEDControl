import json
import os
# Path to the settings.json file
script_dir = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(script_dir, "settings.json")

with open(settings_path, "r") as f:
    data = json.load(f)
    devices = data["devices"]
    lighting_groups = data["lighting_groups"]
    scenes = data["scenes"]