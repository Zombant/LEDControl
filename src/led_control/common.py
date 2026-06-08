import json
import os
from pathlib import Path
from enum import Enum

################################################################
##                       Constants                            ##
################################################################
services = ["wiz", "wled", "openrgb"]

################################################################
##                      Exceptions                            ##
################################################################

class InvalidDeviceException(Exception):
    pass

class InvalidSceneException(Exception):
    pass

class NoRGBException(Exception):
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
    # Filter for enabled devices
    devices = {
        name: details for name, details in devices.items()
        if details.get("enabled") == True
    }
    lighting_groups = data["lighting_groups"]
    scenes = data["scenes"]

################################################################
## TODO: Functions to modify settings.json (add/remove things)##
## Default wiz scenes will be read-only                       ##
################################################################


################################################################
##                      Common Functions                      ##
################################################################

def check_device_valid(devices_to_check: list[str]):
    for device in devices_to_check:
        if device not in devices:
            raise InvalidDeviceException(f"Device {device} not found.")
        if devices[device]['service'] not in services:
            raise InvalidDeviceException(f"Service {devices[device]['service']} is unknown.")
        
def check_scene_valid(scene_name: str):
    if scene_name not in scenes.keys():
        raise InvalidSceneException(f"Scene {scene_name} not found.")

def check_service_valid(device_to_check: str, service_name: str):
    if devices[device_to_check]['service'] != service_name:
        raise InvalidDeviceException(f"This function is incompatable with {service_name}.")

def check_device_is_light(devices_to_check: list[str]):
    for device in devices_to_check:
        if devices[device]['type'] == 'outlet':
            raise InvalidDeviceException(f"Device {device} is not a light.")

def percent_to_byte(percent: int):
    return int(percent / 100 * 255)

def byte_to_percent(byte: int):
    return int(byte / 255 * 100)