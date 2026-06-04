from enum import Enum

from fastapi import FastAPI, HTTPException
import uvicorn

import led_control
from led_control import *
from common import *

# Limit the choosable items in the Swagger UI (creates a dropdown)
DevicesEnum = Enum("DevicesEnum", {device_name: device_name for device_name in devices.keys()})
ScenesEnum = Enum("ScenesEnum", {scene_name: scene_name for scene_name in scenes.keys()})

app = FastAPI()

@app.get("/list/devices")
async def list_devices():
    return {"devices": get_devices()}

@app.get("/list/groups")
async def list_groups():
    return {"groups": get_groups()}

@app.get("/list/scenes")
async def list_scenes():
    return {"scenes": get_scenes()}



@app.get("/device/{device}/state")
async def get_device_state(device: DevicesEnum):
    try:
        return {"state": get_state(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/brightness")
async def get_device_brightness(device: DevicesEnum):
    try:
        return {"brightness": get_brightness(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/rgb")
async def get_device_state(device: DevicesEnum):
    try:
        return {"rgb": get_rgb(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NoRGBException as e:
        raise HTTPException(status_code=405, detail="This device does not currently have RGB values. It may be in scene mode or offline.")

@app.get("/device/{device}/scene")
async def get_device_scene(device: DevicesEnum):
    try:
        return {"scene": get_scene(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/effect")
async def get_device_effect(device: DevicesEnum):
    try:
        return {"effect": get_effect(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/effects")
async def get_device_effects(device: DevicesEnum):
    try:
        return {"effects": get_effects(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/palettes")
async def get_device_palettes(device: DevicesEnum):
    try:
        return {"palettes": get_palettes(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/palette")
async def get_device_palette(device: DevicesEnum):
    try:
        return {"palette": get_palette(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/speed")
async def get_device_speed(device: DevicesEnum):
    try:
        return {"speed": get_speed(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/device/{device}/intensity")
async def get_device_intensity(device: DevicesEnum):
    try:
        return {"intensity": get_intensity(device.value)}
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/device/{device}/state")
async def set_device_state(device: DevicesEnum, state: bool):
    try:
        set_state([device.value], state)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/device/{device}/brightness")
async def set_device_brightness(device: DevicesEnum, brightness: int):
    try:
        set_brightness([device.value], brightness)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/device/{device}/rgb")
async def set_device_rgb(device: DevicesEnum, r: int, g: int, b: int):
    try:
        set_rgb([device.value], r, g, b)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/device/{device}/scene")
async def set_device_scene(device: DevicesEnum, scene: ScenesEnum):
    try:
        set_scene([device.value], scene.value)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSceneException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/device/{device}/effect")
async def set_device_effect(device: DevicesEnum, effect: int):
    try:
        set_effect([device.value], effect)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))    

@app.post("/device/{device}/palette")
async def set_device_palette(device: DevicesEnum, palette: int):
    try:
        set_palette([device.value], palette)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/device/{device}/speed")
async def set_device_speed(device: DevicesEnum, speed: int):
    try:
        set_speed([device.value], speed)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/device/{device}/intensity")
async def set_device_intensity(device: DevicesEnum, intensity: int):
    try:
        set_intensity([device.value], intensity)
    except InvalidDeviceException as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    # Set up OpenRGB
    start_openrgb_server()

    uvicorn.run(app, host="0.0.0.0", port=8000)