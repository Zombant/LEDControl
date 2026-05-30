#!/usr/bin/env python3

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
import socket
import subprocess
import time
import argparse
import sys
import openrgb

host = "localhost"
port = 6742

# Check on process:
# sudo ss -tulpn | grep :6742

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

def set_state(device, state):
    if state == True:
        device.set_color(RGBColor(128, 128, 128))
    else:
        device.set_color(RGBColor(0, 0, 0))

def set_rgb(device, r, g, b):
    device.set_color(RGBColor(r, g, b))

def set_color(device, color):
    device.set_color(color)

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
            factor = max(0, int(args.params[0])) / 100.0
            current_colors = motherboard.colors[0]
            new_colors = RGBColor(
                min(255, int(current_colors.red * factor)),
                min(255, int(current_colors.green * factor)),
                min(255, int(current_colors.blue * factor))
            )
            set_color(device, new_colors)

        else:
            print_help(parser)
    
    else:
        print_help(parser)