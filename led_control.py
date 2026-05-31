from common import devices, scenes, lighting_groups
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

def set_state(devices_list, state):
    for device in devices_list:
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_state(devices[device]['ip'], state)
            #test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            wled_control.set_light_state(devices[device]['ip'], state)
        elif devices[device]['service'] == "openrgb":
            openrgb_control.set_state(openrgb_client.get_devices_by_name(devices[device]['ip'])[0], state)

def set_brightness(devices_list, brightness):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            result_code = wiz_control.set_light_dimming(devices[device]['ip'], brightness)
            #test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            wled_control.set_light_brightness(devices[device]['ip'], (((brightness - 0) / (100 - 0)) * (255 - 0)))

# Scenes are only available on wiz devices but are emulated for RGB devices
def set_scene(devices_list, scene_data):
    for device in devices_list:
        if devices[device]['type'] != "light":
            continue
        if devices[device]['service'] == "wiz":
            # Handle custom scenes
            if scene_data["wiz_id"] == -1:
                result_code = wiz_control.set_light_rgb(devices[device]['ip'], scene_data["r"], scene_data["g"], scene_data["b"])
            else:
                result_code = wiz_control.set_light_scene(devices[device]['ip'], scene_data["wiz_id"])
            #test_result_code(result_code, device.replace('_', ' ').title())
        elif devices[device]['service'] == "wled":
            r, g, b = scene_data["r"], scene_data["g"], scene_data["b"]
            wled_control.set_light_effect(devices[device]['ip'], 0) # Set effect to "Solid"
            wled_control.set_light_rgb(devices[device]['ip'], r, g, b)
        elif devices[device]['service'] == "openrgb":
            r, g, b = scene_data["r"], scene_data["g"], scene_data["b"]
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