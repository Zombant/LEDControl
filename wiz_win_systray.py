import pystray
from PIL import Image, ImageDraw
import threading
import os



import wiz_control
from wiz_control import devices, scenes, lighting_groups

if os.name == 'nt':
    import ctypes
    #Set process name for Windows
    ctypes.windll.kernel32.SetConsoleTitleW("WiZ Control")

script_dir = os.path.dirname(os.path.abspath(__file__))

icon = None

def test_result_code(result_code, title):
    global icon
    if result_code == 1:
        icon.notify(f"Error sending command", title)
    if result_code == 2:
        icon.notify(f"Failed to send command after {wiz_control.retry_count} attempts", title)

def set_state(devices_list, state):
    for device in devices_list:
        result_code = wiz_control.set_light_state(devices[device]['ip'], state)
        test_result_code(result_code, device.replace('_', ' ').title())

def set_scene(devices_list, scene_id):
    for device in devices_list:
        result_code = wiz_control.set_light_scene(devices[device]['ip'], scene_id)
        test_result_code(result_code, device.replace('_', ' ').title())

def set_dimmer(devices_list, dimmer):
    for device in devices_list:
        result_code = wiz_control.set_light_dimming(devices[device]['ip'], dimmer)
        test_result_code(result_code, device.replace('_', ' ').title())

# Load light bulb image for the system tray icon
def create_light_bulb_image(height, width):
    image = Image.open(os.path.join(script_dir, "light_bulb.png"))
    #image = image.resize((width, height))
    return image

# Helper function to create a menu item for a scene for a group
def create_group_scene_menu_item(group, scene):
    return pystray.MenuItem(scene.replace('_', ' ').title(), lambda: set_scene(lighting_groups[group], scenes[scene]))

# Helper function to create a menu item for a scene for a device
def create_device_scene_menu_item(device, scene):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(scene.replace('_', ' ').title(), lambda: set_scene([device], scenes[scene])) 

def create_device_dimmer_menu_item(device, dimmer):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(f"{dimmer}%", lambda: set_dimmer([device], dimmer))

def create_group_dimmer_menu_item(group, dimmer):
    return pystray.MenuItem(f"{dimmer}%", lambda: set_dimmer(lighting_groups[group], dimmer))

# Helper function to create a menu item for a lighting group
def create_group_menu_item(group):
    return pystray.MenuItem(group.replace('_', ' ').title(), pystray.Menu(
        pystray.MenuItem(f"{group.replace('_', ' ').title()} On", lambda: set_state(lighting_groups[group], True)),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Off", lambda: set_state(lighting_groups[group], False)),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Scene", pystray.Menu(
            *[create_group_scene_menu_item(group, scene) for scene in scenes]
        )),
        pystray.MenuItem(f"{group.replace('_', ' ').title()} Dimmer", pystray.Menu(
            *[create_group_dimmer_menu_item(group, dimmer) for dimmer in range(10, 101, 10)]
        ))
    ))

# Helper function to create a menu item for a device
def create_device_menu_item(device):
    menu = []
    menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} On", lambda: set_state([device], True)))
    menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Off", lambda: set_state([device], False)))
    if devices[device]['type'] == 'light':
        menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Scene", pystray.Menu(
            *[create_device_scene_menu_item(device, scene) for scene in scenes]
        )))
        menu.append(pystray.MenuItem(f"{device.replace('_', ' ').title()} Dimmer", pystray.Menu(
            *[create_device_dimmer_menu_item(device, dimmer) for dimmer in range(10, 101, 10)]
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
