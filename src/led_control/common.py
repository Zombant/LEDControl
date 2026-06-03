import json
import os
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent.parent

# Path to the settings.json file
settings_path = os.path.join(project_dir, "settings.json")

with open(settings_path, "r") as f:
    data = json.load(f)
    devices = data["devices"]
    lighting_groups = data["lighting_groups"]
    scenes = data["scenes"]