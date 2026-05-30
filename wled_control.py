#!/usr/bin/env python3

import requests
import json
from time import sleep
import sys
import argparse

from common import devices, lighting_groups

# Filter for only WLED devices
devices = {
    name: details for name, details in devices.items() 
    if details.get("service") == "wled"
}

def send_command(ip, payload):
    try:
        response = requests.post(f"http://{ip}/json/state", json=payload)
        response.raise_for_status()
        print(f"Sent payload {payload} to {ip}")
    except:
        print("Failed to send command")

def set_light_state(ip, state):
    payload = {"on": state}
    send_command(ip, payload)

def get_light_palettes(ip):
    try:
        response = requests.get(f"http://{ip}/json/pal")
        response.raise_for_status()

        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to get palettes for {ip}: {e}")
        return None

def set_light_palette(ip, palette_idx):
    payload = {
        "seg": [
            {
                "pal": int(palette_idx)
            }
        ]
    }
    send_command(ip, payload)

def get_light_effects(ip):
    try:
        response = requests.get(f"http://{ip}/json/eff")
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to get effects for {ip}: {e}")
        return None

def set_light_effect(ip, effect_idx, effect_speed=100, effect_intensity=255):
    payload = {
        "seg": [
            {
                "fx": int(effect_idx),
                "sx": int(effect_speed),
                "ix": int(effect_intensity)
            }
        ]
    }
    send_command(ip, payload)

def set_light_brightness(ip, brightness):
    brightness = max(0, min(255, int(brightness)))
    
    payload = {"bri": brightness}
    send_command(ip, payload)

def get_light_state(ip):
    try:
        response = requests.get(f"http://{ip}/json/state")
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to get status for {ip}: {e}")
        return None

def get_light_status(ip):
    get_light_state(ip).get("on")

def set_light_rgb(ip, r, g, b):
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    payload = {
        "seg": [
            {
                "col": [
                    [r, g, b]
                ]
            }
        ]
    }
    send_command(ip, payload)

# Works with both 0-255 and 1900-10091
def set_light_temp(ip, temp):
    payload = {
        "seg": [
            {
                "cct": temp
            }
        ]
    }
    send_command(ip, payload)

def list_devices():
    for name, _ in devices.items():
        print(name)

def list_scenes():
    for name, _ in scenes.items():
        print(name)

def list_groups():
    for name, _ in lighting_groups.items():
        print(name)

# TODO: Command line args