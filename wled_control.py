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

def set_light_effect(ip, effect_idx):
    payload = {
        "seg": [
            {
                "fx": int(effect_idx)
            }
        ]
    }
    send_command(ip, payload)

def set_effect_speed(ip, effect_speed):
    payload = {
        "seg": [
            {
                "sx": int(effect_speed)
            }
        ]
    }
    send_command(ip, payload)

def set_effect_intensity(ip, effect_intensity):
    payload = {
        "seg": [
            {
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

def list_effects(device):
    if device not in devices.keys():
        print(f"{device} is not a valid device")
        return
    for name in get_light_effects(devices[device]["ip"]):
        print(name)

def list_palettes(device):
    if device not in devices.keys():
        print(f"{device} is not a valid device")
        return
    for name in get_light_palettes(devices[device]["ip"]):
        print(name)

def list_groups():
    for name, _ in lighting_groups.items():
        print(name)

def print_help(parser):
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control WLED lights")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List devices, effects, palettes, or groups")
    list_parser.add_argument("type", choices=["devices", "effects", "palettes", "groups"], help="Type to list")
    list_parser.add_argument("params", nargs="*", help="Device name")

    device_parser = subparsers.add_parser("control", help="Control a device")
    device_parser.add_argument("name", help="Device name")
    device_parser.add_argument("action", choices=["state", "brightness", "rgb", "temp", "effect", "palette", "speed", "intensity", "status"], help="Action to perform")
    device_parser.add_argument("params", nargs="*", help="Parameters for the action")

    args = parser.parse_args()

    if args.command == "list":
        if args.type == "devices":
            list_devices()
        elif args.type == "effects" and len(args.params) > 0:
            list_effects(args.params[0])
        elif args.type == "palettes" and len(args.params) > 0:
            list_palettes(args.params[0])
        elif args.type == "groups":
            list_groups()
        else:
            print_help(parser)
    
    elif args.command == "control":
        if args.name not in devices:
            print(f"{args.name} is not a valid device")
            print_help(parser)

        ip = devices[args.name]['ip']

        if args.action == "state":
            if len(args.params) != 1 or args.params[0] not in ["on", "off"]:
                print_help(parser)
            else:
                state = True if args.params[0] == "on" else False
                set_light_state(ip, state)
        
        elif args.action == "brightness":
            if len(args.params) != 1:
                print_help(parser)
            elif int(args.params[0]) < 0 or int(args.params[0]) > 255:
                print("Brightness must be in range 0-255")
                exit(1)
            set_light_brightness(ip, int(args.params[0]))
        
        elif args.action == "rgb":
            if len(args.params) != 3:
                print_help(parser)
            r, g, b = map(int, args.params[:3])
            set_light_rgb(ip, r, g, b)
        
        elif args.action == "temp":
            if len(args.params) != 1:
                print_help(parser)
            set_light_temp(ip, int(args.params[0]))
        
        ## TODO: Effects and palettes
        
        elif args.action == "speed":
            if len(args.params) != 1:
                print_help(parser)
            set_effect_speed(ip, int(args.params[0]))
            
        elif args.action == "intensity":
            if len(args.params) != 1:
                print_help(parser)
            set_effect_intensity(ip, int(args.params[0]))

        elif args.action == "status":
            status = get_light_state(ip)
            if status:
                print(json.dumps(status, indent=4))
        
        else:
            print_help(parser)
    
    else:
        print_help(parser)