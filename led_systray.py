import pystray
from PIL import Image, ImageDraw
import threading
import os
import wiz_control
from wiz_control import scenes as wiz_scenes
import wled_control
import openrgb_control
from common import devices, lighting_groups
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
import socket


if os.name == 'nt':
    import ctypes
    #Set process name for Windows
    ctypes.windll.kernel32.SetConsoleTitleW("LED Control")

script_dir = os.path.dirname(os.path.abspath(__file__))

icon = None

openrgb_client = None

# Define RGB values to match WiZ scenes
# A scene is essentially a preset color
# TODO: Omit id to indicate to WiZ to use the RGB values, not the id for custom presets
WIZ_SCENES = {
    "cozy": {
        "id": 6, 
        "r": 255, "g": 147, "b": 41
    },
    "warm_white": {
        "id": 11, 
        "r": 255, "g": 162, "b": 70
    },
    "daylight": {
        "id": 12, 
        "r": 255, "g": 180, "b": 107
    },
    "cool_white": {
        "id": 13, 
        "r": 255, "g": 232, "b": 214
    },
    "night_light": {
        "id": 14, 
        "r": 48, "g": 27, "b": 8
    },
    "focus": {
        "id": 15, 
        "r": 255, "g": 244, "b": 148
    },
    "relax": {
        "id": 16, 
        "r": 255, "g": 84, "b": 115
    },
    "true_colors": {
        "id": 17, 
        "r": 255, "g": 152, "b": 49
    },
    "tv_time": {
        "id": 18, 
        "r": 56, "g": 32, "b": 145
    },
    "plant_growth": {
        "id": 19, 
        "r": 215, "g": 0, "b": 155
    }
}

# Load light bulb image for the system tray icon
def create_light_bulb_image(height, width):
    image = Image.open(os.path.join(script_dir, "light_bulb.png"))
    #image = image.resize((width, height))
    return image

def test_result_code(result_code, title):
    global icon
    if result_code == 1:
        icon.notify(f"Error sending command", title)
    if result_code == 2:
        icon.notify(f"Failed to send command after {wiz_control.retry_count} attempts", title)

################################################################
## These functions actually perform the action on the devices ##
## Here is where the action is chosen for the service         ##
################################################################

def set_state(devices_list, state):
    for device in devices_list:
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_state(devices[device]['ip'], state)
            test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            wled_control.set_light_state(devices[device]['ip'], state)
        elif devices[device]['service'] == "openrgb":
            # TODO: may not necessarily be motherboard
            openrgb_control.set_state(openrgb_client.get_devices_by_name(devices[device]['ip'])[0], state)

def set_brightness(devices_list, brightness):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_dimming(devices[device]['ip'], brightness)
            test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            wled_control.set_light_brightness(devices[device]['ip'], (((brightness - 0) / (100 - 0)) * (255 - 0)))

# Scenes are only available on wiz devices but are emulated for RGB devices
def set_scene(devices_list, scene_id):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_scene(devices[device]['ip'], scene_id)
            test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            r, g, b = next((d["r"], d["g"], d["b"]) for d in WIZ_SCENES.values() if d["id"] == scene_id)
            wled_control.set_light_effect(devices[device]['ip'], 0) # Set effect to "Solid"
            wled_control.set_light_rgb(devices[device]['ip'], r, g, b)
        elif devices[device]['service'] == "openrgb":
            r, g, b = next((d["r"], d["g"], d["b"]) for d in WIZ_SCENES.values() if d["id"] == scene_id)
            openrgb_control.set_rgb(openrgb_client.get_devices_by_type(DeviceType.MOTHERBOARD)[0], r, g, b)

# Palettes and effects are only available on WLED devices
def set_palette(devices_list, palette_idx):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_light_palette(devices[device]['ip'], palette_idx)

def set_effect(devices_list, effect_idx):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_light_effect(devices[device]['ip'], effect_idx)

def set_speed(devices_list, speed):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_effect_speed(devices[device]['ip'], (((speed - 0) / (100 - 0)) * (255 - 0)))

def set_intensity(devices_list, speed):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_effect_intensity(devices[device]['ip'], (((speed - 0) / (100 - 0)) * (255 - 0)))

###########################################
## Helper functions to create menu items ##
###########################################

# Scenes
def create_scene_select_menu_item(devices, scene):
        return pystray.MenuItem(scene.replace('_', ' ').title(), lambda: set_scene(devices, wiz_scenes[scene]))

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
            *[create_scene_select_menu_item(lighting_groups[group], scene) for scene in wiz_scenes]
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
            *[create_scene_select_menu_item([device], scene) for scene in wiz_scenes]
        )))
        if devices[device]['service'] == "wled":
            menu.append(pystray.Menu.SEPARATOR)
            menu.append(pystray.MenuItem('WLED Only', None, enabled=False))
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Palette", pystray.Menu(
                *[create_palette_select_menu_item([device], palette_name, palette_idx) for palette_idx, palette_name in enumerate(wled_control.get_light_palettes(devices[device]['ip']))]
            )))
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
    openrgb_control.start_openrgb_server()

    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            openrgb_client = OpenRGBClient()
            print("OpenRGB Connected")
            break
        except (ConnectionRefusedError, socket.timeout):
            attempt += 1
            time.sleep(0.5)

    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.start()
