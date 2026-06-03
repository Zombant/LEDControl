import json
import os
from pathlib import Path
from enum import Enum

################################################################
##                      Exceptions                            ##
################################################################

class InvalidDeviceException(Exception):
    pass

class InvalidSceneException(Exception):
    pass

class WLEDOnlyException(Exception):
    pass

class WIZOnlyException(Exception):
    pass

class ServiceNotFoundException(Exception):
    pass

################################################################
##                      Directories                           ##
################################################################

project_dir = Path(__file__).resolve().parent.parent.parent

# Path to the settings.json file
settings_path = os.path.join(project_dir, "settings.json")

with open(settings_path, "r") as f:
    data = json.load(f)
    devices = data["devices"]
    lighting_groups = data["lighting_groups"]
    scenes = data["scenes"]


################################################################
##                      Common Functions                      ##
################################################################

def check_device_valid(devices_to_check: list[str]):
    for device in devices_to_check:
        if device not in devices:
            raise InvalidDeviceException(f"Device {device} not found.")

def check_scene_valid(scene_name: str):
    if scene_name not in scenes.keys():
        raise InvalidSceneException(f"Scene {scene_name} not found.")