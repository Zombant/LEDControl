import pystray
from PIL import Image, ImageDraw
import threading
import os
import wiz_control
from wiz_control import scenes as wiz_scenes
import wled_control
from common import devices, lighting_groups

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

def test_result_code(result_code, title):
    global icon
    if result_code == 1:
        icon.notify(f"Error sending command", title)
    if result_code == 2:
        icon.notify(f"Failed to send command after {wiz_control.retry_count} attempts", title)

################################################################
## These functions actually perform the action on the devices ##
################################################################

def set_state(devices_list, state):
    for device in devices_list:
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_state(devices[device]['ip'], state)
            test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            wled_control.set_light_state(devices[device]['ip'], state)

def set_brightness(devices_list, brightness):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_dimming(devices[device]['ip'], brightness)
            test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            wled_control.set_light_brightness(devices[device]['ip'], (((brightness - 0) / (100 - 0)) * (255 - 0)))

# Scenes are only available on wiz devices
def set_scene(devices_list, scene_id):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_scene(devices[device]['ip'], scene_id)
            test_result_code(result_code, device.replace('_', ' ').title())

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
# TODO: the duplicate functions for device/group can probably be combined

# Scenes
def create_group_scene_menu_item(group, scene):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(scene.replace('_', ' ').title(), lambda: set_scene(lighting_groups[group], wiz_scenes[scene]))

def create_device_scene_menu_item(device, scene):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(scene.replace('_', ' ').title(), lambda: set_scene([device], wiz_scenes[scene])) 

# Brightness
def create_group_brightness_menu_item(group, brightness):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(f"{brightness}%", lambda: set_brightness(lighting_groups[group], brightness))

def create_device_brightness_menu_item(device, brightness):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(f"{brightness}%", lambda: set_brightness([device], brightness))

# Palettes
def create_device_palette_menu_item(device, palette_name, palette_idx):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(palette_name.replace('_', ' ').title(), lambda: set_palette([device], palette_idx))

# Effects
def create_device_effect_menu_item(device, effect_name, effect_idx):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(effect_name.replace('_', ' ').title(), lambda: set_effect([device], effect_idx))

# Effect speed
def create_device_effect_speed_menu_item(device, speed):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(f"{speed}%", lambda: set_speed([device], speed))

# Effect intensity
def create_device_effect_intensity_menu_item(device, intensity):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(f"{intensity}%", lambda: set_intensity([device], intensity))

# Menu for a group
def create_group_menu_item(group):
    return pystray.MenuItem(group.replace('_', ' ').title(), pystray.Menu(
        pystray.MenuItem(f"{group.replace('_', ' ').title()} On", lambda: set_state(lighting_groups[group], True)),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Off", lambda: set_state(lighting_groups[group], False)),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Scene", pystray.Menu(
            *[create_group_scene_menu_item(group, scene) for scene in wiz_scenes]
        )),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Brightness", pystray.Menu(
            *[create_group_brightness_menu_item(group, brightness) for brightness in range(10, 101, 10)]
        ))
    ))

# Menu for a device
def create_device_menu_item(device):
    menu = []
    menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} On", lambda: set_state([device], True)))
    menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Off", lambda: set_state([device], False)))
    if devices[device]['type'] == 'light':
        if devices[device]['service'] == "wiz":
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Scene", pystray.Menu(
                *[create_device_scene_menu_item(device, scene) for scene in wiz_scenes]
            )))
        elif devices[device]['service'] == "wled":
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Palette", pystray.Menu(
                *[create_device_palette_menu_item(device, palette_name, palette_idx) for palette_idx, palette_name in enumerate(wled_control.get_light_palettes(devices[device]['ip']))]
            )))
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Effect", pystray.Menu(
                *[create_device_effect_menu_item(device, effect_name, effect_idx) for effect_idx, effect_name in enumerate(wled_control.get_light_effects(devices[device]['ip']))]
            )))
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Speed", pystray.Menu(
                *[create_device_effect_speed_menu_item(device, speed) for speed in range(10, 101, 10)]
            )))
            menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Intensity", pystray.Menu(
                *[create_device_effect_intensity_menu_item(device, intensity) for intensity in range(10, 101, 10)]
            )))

        menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Brightness", pystray.Menu(
            *[create_device_brightness_menu_item(device, brightness) for brightness in range(10, 101, 10)]
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
    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.start()
