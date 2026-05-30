#!/usr/bin/env python3

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
import socket
import subprocess
import time
import argparse
import sys


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
    cmd = ["openrgb", "--server", "--startminimized"]
    # Windows example:
    # cmd = [r"C:\Program Files\OpenRGB\OpenRGB.exe", "--server", "--startminimized"]

    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    
    # Wait a moment for the server to spin up and bind to the port
    time.sleep(2)
    return process

def set_rgb(device, color):
    device.set_color(color)

def list_devices(client):
    for device in client.devices:
        print(f"id={device.id}\t{device.name}")

def print_help(parser):
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control OpenRGB lights")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List devices")
    list_parser.add_argument("type", choices=["devices"], help="Type to list")

    device_parser = subparsers.add_parser("control", help="Control a device")
    device_parser.add_argument("name", help="Device ID")
    device_parser.add_argument("action", choices=["brightness", "rgb"], help="Action to perform")
    device_parser.add_argument("params", nargs="*", help="Parameters for the action")

    args = parser.parse_args()


    if not is_server_running():
        start_openrgb_server()

    client = OpenRGBClient(host, port)
    devices = client.devices
    motherboard = client.get_devices_by_type(DeviceType.MOTHERBOARD)[0]

    if args.command == "list":
        if args.type == "devices":
            list_devices(client)
        else:
            print_help(parser)

    elif args.command == "control":
        if int(args.name) > len(devices)-1:
            print(f"{args.name} is not a valid device")
            print_help(parser)
        
        device_obj = next((device for device in devices if device.id == int(args.name)), None)
        device = client.get_devices_by_name(device_obj.name)[0]
        if args.action == "rgb":
            if len(args.params) != 3:
                print_help(parser)
            r, g, b = map(int, args.params[:3])
            set_rgb(device, RGBColor(r, g, b))

        if args.action == "brightness":
            if len(args.params) != 1:
                print_help(parser)
            factor = max(0, int(args.params[0])) / 100.0
            current_colors = motherboard.colors[0]
            new_colors = RGBColor(
                min(255, int(current_colors.red * factor)),
                min(255, int(current_colors.green * factor)),
                min(255, int(current_colors.blue * factor))
            )
            print(current_colors)
            print(new_colors)
            print(factor)
            set_rgb(device, new_colors)