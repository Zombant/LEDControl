from common import *
import wiz_control
import wled_control
import openrgb_control

from openrgb import OpenRGBClient
from openrgb.utils import DeviceType

# def test_result_code(result_code, title):
#     global icon
#     if result_code == 1:
#         icon.notify(f"Error sending command", title)
#     if result_code == 2:
#         icon.notify(f"Failed to send command after {wiz_control.retry_count} attempts", title)

# TODO: Move this stuff to openrgb_control
openrgb_client = None

################################################################
##                      Open RGB Server                       ##
################################################################
def start_openrgb_server(max_attempts=10):
    global openrgb_client
    openrgb_control.start_openrgb_server()

    attempt = 0
    while attempt < max_attempts:
        try:
            openrgb_client = OpenRGBClient()
            print("OpenRGB Connected")
            break
        except (ConnectionRefusedError, socket.timeout):
            print(f"Failed to connect: ({attempt}/{max_attempts})")
            attempt += 1
            time.sleep(0.5)


################################################################
## These functions actually perform the action on the devices ##
## in the given list, regardless of the service it uses.      ##
################################################################

def is_online(device):
    check_device_valid([device])
    if devices[device]['service'] == "wiz":
        result_code = wiz_control.get_light_status(devices[device]['ip'])
        if result_code == 1 or result_code == 2:
            print(f"{device} is not online or not responding")
            return False
        else:
            return True
    elif devices[device]['service'] == "wled":
        result = wled_control.get_light_status(devices[device]['ip'])
        if result == None:
            print(f"{device} is not online or not responding")
            return False
        else:
            return True
    elif devices[device]['service'] == "openrgb":
        devices_list = openrgb_client.get_devices_by_name(devices[device]['ip'])
        if len(devices_list) == 0:
            return False
        else:
            return True
    else:
        raise ServiceNotFoundException()


################################################################
##                         Getters                            ##
################################################################

def get_devices():
    return devices.items()

def get_groups():
    return lighting_groups.items()

def get_scenes():
    return scenes.items()

def get_paletttes(device):
    check_device_valid([device])
    if devices[device]['service'] == "wled":
        return wled_control.get_light_palettes(devices[device]['ip'])
    else:
        raise WLEDOnlyException()

def get_effects(device):
    check_device_valid([device])
    if devices[device]['service'] == "wled":
        return wled_control.get_light_effects(devices[device]['ip'])
    else:
        raise WLEDOnlyException()

def get_state(device):
    check_device_valid([device])
    if devices[device]['service'] == "wiz":
        return wiz_control.get_light_state(devices[device]['ip'])
    elif devices[device]['service'] == "wled":
        return wled_control.get_light_state(devices[device]['ip'])
    elif devices[device]['service'] == "openrgb":
        return openrgb_control.get_state(openrgb_client.get_devices_by_name(devices[device]['ip'])[0])
    else:
        raise ServiceNotFoundException()

def get_brightness(device):
    check_device_valid([device])
    if devices[device]['service'] == "wiz":
        return wiz_control.get_light_brightness(devices[device]['ip'])
    elif devices[device]['service'] == "wled":
        bri = wled_control.get_light_brightness(devices[device]['ip'])
        return int((((bri - 0) / (255 - 0)) * (100 - 0)))
    elif devices[device]['service'] == "openrgb":
        return NotImplementedError
    else:
        raise ServiceNotFoundException()

def get_rgb(device):
    check_device_valid([device])
    if devices[device]['service'] == "wiz":
        return wiz_control.get_light_rgb(devices[device]['ip'])
    elif devices[device]['service'] == "wled":
        return wled_control.get_light_rgb(devices[device]['ip'])
    elif devices[device]['service'] == "openrgb":
        return openrgb_control.get_rgb(openrgb_client.get_devices_by_name(devices[device]['ip'])[0])
    else:
        raise ServiceNotFoundException()

# For WiZ, the scene will be directly checked. For others, the rgb associated with that scene will be checked
def get_scene(device):
    check_device_valid([device])
    if devices[device]['service'] == "wiz":
        scene_id = wiz_control.get_light_scene(devices[device]['ip'])
        # Check if this was a custom scene and if so, check via rgb:
        if scene_id == 0:
            rgb = wiz_control.get_light_rgb(devices[device]['ip'])
            return next((scene_name for scene_name, scene_data in scenes.items() if scene_data["r"] == rgb[0] and scene_data["g"] == rgb[1] and scene_data["b"] == rgb[2]), None)
        else:
            return next((scene_name for scene_name, scene_data in scenes.items() if scenes[scene_name]["wiz_id"] == scene_id), None)
    elif devices[device]['service'] == "wled":
        rgb = wled_control.get_light_rgb(devices[device]['ip'])
        return next((scene_name for scene_name, scene_data in scenes.items()
            if scene_data["r"] == rgb[0] and scene_data["g"] == rgb[1] and scene_data["b"] == rgb[2]), None)

    elif devices[device]['service'] == "openrgb":
        rgb = openrgb_control.get_rgb(openrgb_client.get_devices_by_name(devices[device]['ip'])[0])
        return next((scene_name for scene_name, scene_data in scenes.items()
            if scene_data["r"] == rgb[0] and scene_data["g"] == rgb[1] and scene_data["b"] == rgb[2]), None)
    else:
        raise ServiceNotFoundException()


def get_effect(device):
    check_device_valid([device])
    if devices[device]['service'] == "wled":
        return wled_control.get_light_effect(devices[device]['ip'])
    else:
        raise WLEDOnlyException()

def get_palette(device):
    check_device_valid([device])
    if devices[device]['service'] == "wled":
        return wled_control.get_light_palette(devices[device]['ip'])
    else:
        raise WLEDOnlyException()

def get_speed(device):
    check_device_valid([device])
    if devices[device]['service'] == "wled":
        return wled_control.get_light_speed(devices[device]['ip'])
    else:
        raise WLEDOnlyException()

def get_intensity(device):
    check_device_valid([device])
    if devices[device]['service'] == "wled":
        return wled_control.get_light_intensity(devices[device]['ip'])
    else:
        raise WLEDOnlyException()


################################################################
##                         Setters                            ##
################################################################

def set_state(devices_list, state):
    check_device_valid(devices_list)
    for device in devices_list:
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_state(devices[device]['ip'], state)
        elif devices[device]['service'] == "wled":
            wled_control.set_light_state(devices[device]['ip'], state)
        elif devices[device]['service'] == "openrgb":
            openrgb_control.set_state(openrgb_client.get_devices_by_name(devices[device]['ip'])[0], state)

def set_brightness(devices_list, brightness):
    check_device_valid(devices_list)
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_brightness(devices[device]['ip'], brightness)
        elif devices[device]['service'] == "wled":
            wled_control.set_light_brightness(devices[device]['ip'], (((brightness - 0) / (100 - 0)) * (255 - 0)))
        elif devices[device]['service'] == "openrgb":
            openrgb_control.set_brightness(openrgb_client.get_devices_by_name(devices[device]['ip'])[0], brightness)

def set_rgb(devices_list, r, g, b):
    raise NotImplementedError

# Scenes are only available on wiz devices but are emulated for RGB devices
def set_scene(devices_list, scene_name):
    check_device_valid(devices_list)
    check_scene_valid(scene_name)
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            # Handle custom scenes
            if scenes[scene_name]["wiz_id"] == -1:
                result_code = wiz_control.set_light_rgb(devices[device]['ip'], scenes[scene_name]["r"], scenes[scene_name]["g"], scenes[scene_name]["b"])
            else:
                result_code = wiz_control.set_light_scene(devices[device]['ip'], scenes[scene_name]["wiz_id"])
        elif devices[device]['service'] == "wled":
            r, g, b = scenes[scene_name]["r"], scenes[scene_name]["g"], scenes[scene_name]["b"]
            wled_control.set_light_effect(devices[device]['ip'], 0) # Set effect to "Solid"
            wled_control.set_light_rgb(devices[device]['ip'], r, g, b)
        elif devices[device]['service'] == "openrgb":
            r, g, b = scenes[scene_name]["r"], scenes[scene_name]["g"], scenes[scene_name]["b"]
            openrgb_control.set_rgb(openrgb_client.get_devices_by_name(devices[device]['ip'])[0], r, g, b)

# Palettes and effects are only available on WLED devices
def set_effect(devices_list: list[str], effect_idx):
    check_device_valid(devices_list)
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_light_effect(devices[device]['ip'], effect_idx)

def set_palette(devices_list, palette_idx):
    check_device_valid(devices_list)
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_light_palette(devices[device]['ip'], palette_idx)

def set_speed(devices_list, speed):
    check_device_valid(devices_list)
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_effect_speed(devices[device]['ip'], (((speed - 0) / (100 - 0)) * (255 - 0)))

def set_intensity(devices_list, speed):
    check_device_valid(devices_list)
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wled":
            wled_control.set_effect_intensity(devices[device]['ip'], (((speed - 0) / (100 - 0)) * (255 - 0)))