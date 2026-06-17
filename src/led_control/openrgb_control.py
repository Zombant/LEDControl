#!/usr/bin/env python3

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
from common import *
import socket
import subprocess
import time
import argparse
import sys
import colorsys
import openrgb

################################################################
##                   OpenRGB Server Setup                     ##
################################################################

host = "0.0.0.0"
port = 6742

# Keeps track of the current color (hue and saturation) for brightness adjustments
hue_sat_dict = {}

def is_server_running(host=host, port=port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False

def start_openrgb_server():
    if is_server_running():
        return
    cmd = ["openrgb", "--server", "--startminimized"]
    # Windows example:
    # cmd = [r"C:\Program Files\OpenRGB\OpenRGB.exe", "--server", "--startminimized"]
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    return process

################################################################
##                         Getters                            ##
################################################################

def get_state(device):
    if all(colors == RGBColor(0, 0, 0) for colors in device.colors):
        return False
    else:
        return True

def get_brightness(device):
    r, g, b = device.colors[0].red, device.colors[0].green, device.colors[0].blue
    _, _, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return percent_to_byte(v * 100)

def get_rgb(device):
    return (device.colors[0].red, device.colors[0].green, device.colors[0].blue)

def set_state(device, state):
    # If the device is already on and set state is True, return to avoid resetting brightness
    if get_state(device) and state:
        return
    if state == True:
        # If there is a color saved, use that
        if device.name in hue_sat_dict.keys():
            h = hue_sat_dict.get(device.name).get("h")
            s = hue_sat_dict.get(device.name).get("s")
            v = 1
            hue_sat_dict.update({device.name: {"h": h, "s": s, "v": v}})
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            device.set_color(RGBColor(int(r*255), int(g*255), int(b*255)))
        else:
            r = 255; g = 255; b = 255
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            hue_sat_dict.update({device.name: {"h": h, "s": s, "v": v}})

            device.set_color(RGBColor(r, g, b))
    else:
        set_brightness(device, 0)

################################################################
##                         Setters                            ##
################################################################

def set_brightness(device, brightness):
    brightness = max(0, min(255, int(brightness)))
    # If this device already has a hue and saturation saved, use that. Otherwise poll for color
    if device.name in hue_sat_dict.keys():
        h = hue_sat_dict.get(device.name).get("h")
        s = hue_sat_dict.get(device.name).get("s")
    else:
        r, g, b = device.colors[0].red, device.colors[0].green, device.colors[0].blue
        h, s, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    # Brightness is value
    v = brightness / 255
    hue_sat_dict.update({device.name: {"h": h, "s": s, "v": v}})

    # Convert back to rgb
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    device.set_color(RGBColor(int(r*255), int(g*255), int(b*255)))

def set_rgb(device, r, g, b):
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))

    # Save the hue and saturation to avoid quantizing of values
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # If this device already has a color value (brightness) saved, use that
    if device.name in hue_sat_dict.keys():
        v = hue_sat_dict.get(device.name).get("v")

    hue_sat_dict.update({device.name: {"h": h, "s": s, "v": v}})
    # Convert back to rgb
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    device.set_color(RGBColor(int(r*255), int(g*255), int(b*255)))

################################################################
##                   Command-line Interface                   ##
################################################################

def list_devices(client):
    for device in client.devices:
        print(f"id={device.id}\t{device.name}")

def get_device_by_id(client, device_id):
    devices = client.devices
    device_obj = next((device for device in devices if device.id == device_id), None)
    return client.get_devices_by_name(device_obj.name)[0]
    
def print_help(parser):
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control OpenRGB lights")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List devices")
    list_parser.add_argument("type", choices=["devices"], help="Type to list")

    device_parser = subparsers.add_parser("control", help="Control a device")
    device_parser.add_argument("name", help="Device ID or \'motherboard\'")
    device_parser.add_argument("action", choices=["brightness", "rgb"], help="Action to perform")
    device_parser.add_argument("params", nargs="*", help="Parameters for the action")

    args = parser.parse_args()

    start_openrgb_server()
    
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            client = OpenRGBClient()
            print("OpenRGB Connected")
            break
        except (ConnectionRefusedError, socket.timeout):
            attempt += 1
            time.sleep(0.5)

    devices = client.devices

    if args.command == "list":
        if args.type == "devices":
            list_devices(client)
        else:
            print_help(parser)

    elif args.command == "control":
        if args.name == "motherboard":
            device = client.get_devices_by_type(DeviceType.MOTHERBOARD)[0]
        elif int(args.name) > len(devices)-1:
            print(f"{args.name} is not a valid device")
            print_help(parser)
        else:
            device = get_device_by_id(client, int(args.name[0]))


        if args.action == "rgb":
            if len(args.params) != 3:
                print_help(parser)
            r, g, b = map(int, args.params[:3])
            set_rgb(device, r, g, b)

        elif args.action == "brightness":
            if len(args.params) != 1:
                print_help(parser)
            set_brightness(motherboard, args.params[0])

        else:
            print_help(parser)
    
    else:
        print_help(parser)