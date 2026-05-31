import pystray
from PIL import Image, ImageDraw
import threading
import os
import socket

import led_control
from led_control import *

import wled_control

from common import devices, scenes, lighting_groups

if os.name == 'nt':
    import ctypes
    #Set process name for Windows
    ctypes.windll.kernel32.SetConsoleTitleW("LED Control")

script_dir = os.path.dirname(os.path.abspath(__file__))

icon = None


# Load light bulb image for the system tray icon
def create_light_bulb_image(height, width):
    image = Image.open(os.path.join(script_dir, "light_bulb.png"))
    #image = image.resize((width, height))
    return image

###########################################
## Helper functions to create menu items ##
###########################################

# Scenes
def create_scene_select_menu_item(devices, scene_name):
    return pystray.MenuItem(scene_name.replace('_', ' ').title(), lambda: set_scene(devices, scenes[scene_name]))

# Brightness
def create_brightness_select_menu_item(devices, brightness):
    return pystray.MenuItem(f"{brightness}%", lambda: set_brightness(devices, brightness))

# Palettes
def create_palette_select_menu_item(devices, palette_name, palette_idx):
    return pystray.MenuItem(palette_name.replace('_', ' ').title(), lambda: set_palette(devices, palette_idx))

# Effects
def create_effect_select_menu_item(devices, effect_name, effect_idx):
    return pystray.MenuItem(effect_name.replace('_', ' ').title(), lambda: set_effect(devices, effect_idx))

# Effect speed
def create_speed_select_menu_item(devices, speed):
    return pystray.MenuItem(f"{speed}%", lambda: set_speed(devices, speed))

# Effect intensity
def create_intensity_select_menu_item(devices, intensity):
    return pystray.MenuItem(f"{intensity}%", lambda: set_intensity(devices, intensity))

# Menu for a group
def create_group_menu_item(group):
    first_wled_ip = next((info["ip"] for info in devices.values() if info.get("service") == "wled"), None)
    return pystray.MenuItem(group.replace('_', ' ').title(), pystray.Menu(
        pystray.MenuItem(f"{group.replace('_', ' ').title()} On", lambda: set_state(lighting_groups[group], True)),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Off", lambda: set_state(lighting_groups[group], False)),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Brightness", pystray.Menu(
            *[create_brightness_select_menu_item(lighting_groups[group], brightness) for brightness in range(10, 101, 10)]
        )),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Scene", pystray.Menu(
            *[create_scene_select_menu_item(lighting_groups[group], scene_name) for scene_name in scenes]
        )),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('WLED Only', None, enabled=False),
        # This assumes all WLEDs have the same set of palettes and effects
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Palette", pystray.Menu(
            *[create_palette_select_menu_item(lighting_groups[group], palette_name, palette_idx) for palette_idx, palette_name in enumerate(wled_control.get_light_palettes(first_wled_ip))]
        )),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Effect", pystray.Menu(
            *[create_effect_select_menu_item(lighting_groups[group], effect_name, effect_idx) for effect_idx, effect_name in enumerate(wled_control.get_light_effects(first_wled_ip))]
        )),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Speed", pystray.Menu(
            *[create_speed_select_menu_item(lighting_groups[group], speed) for speed in range(10, 101, 10)]
        )),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Intensity", pystray.Menu(
            *[create_intensity_select_menu_item(lighting_groups[group], intensity) for intensity in range(10, 101, 10)]
        ))
    ))

# Menu for a device
def create_device_menu_item(device):
    menu = []
    menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} On", lambda: set_state([device], True)))
    menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Off", lambda: set_state([device], False)))
    if devices[device]['type'] == 'light':
        menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Brightness", pystray.Menu(
            *[create_brightness_select_menu_item([device], brightness) for brightness in range(10, 101, 10)]
        )))
        menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Scene", pystray.Menu(
            *[create_scene_select_menu_item([device], scene_name) for scene_name in scenes]
        )))
        if devices[device]['service'] == "wled":
            menu.append(pystray.Menu.SEPARATOR)
            menu.append(pystray.MenuItem('WLED Only', None, enabled=False))
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Palette", pystray.Menu(
                *[create_palette_select_menu_item([device], palette_name, palette_idx) for palette_idx, palette_name in enumerate(wled_control.get_light_palettes(devices[device]['ip']))]
            )))
            # TODO: This line will fail if WLED device is not on
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Effect", pystray.Menu(
                *[create_effect_select_menu_item([device], effect_name, effect_idx) for effect_idx, effect_name in enumerate(wled_control.get_light_effects(devices[device]['ip']))]
            )))
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Speed", pystray.Menu(
                *[create_speed_select_menu_item([device], speed) for speed in range(10, 101, 10)]
            )))
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Intensity", pystray.Menu(
                *[create_intensity_select_menu_item([device], intensity) for intensity in range(10, 101, 10)]
            )))
    return pystray.MenuItem(device.replace('_', ' ').title(), pystray.Menu(*menu))

# Function to setup the system tray icon
def setup_tray():
    global icon
    icon = pystray.Icon("WiZControl")
    icon.title = "WiZ Control"
    icon.icon = create_light_bulb_image(64, 64)

    menu_items = []

    # Create a submenu for each device
    [menu_items.append(create_device_menu_item(device)) for device in devices]

    menu_items.append(pystray.Menu.SEPARATOR)
    
    # Create a submenu for each lighting group
    [menu_items.append(create_group_menu_item(group)) for group in lighting_groups]

    menu_items.append(pystray.Menu.SEPARATOR)

    menu_items.append(pystray.MenuItem('Quit', lambda: icon.stop()))
    
    icon.menu = pystray.Menu(*menu_items)
    icon.run()
    

# Run the system tray icon in a separate thread
if __name__ == "__main__":
    
    # Set up OpenRGB
    start_openrgb_server()

    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.start()
