from fastapi import FastAPI
import uvicorn

import led_control
from led_control import *
from common import devices, scenes, lighting_groups, project_dir


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
async def get_device_state(device):
    return {"state": get_state(device)}

@app.get("/device/{device}/rgb")
async def get_device_state(device):
    return {"state": get_rgb(device)}

@app.get("/device/{device}/scene")
async def get_device_scene(device):
    return {"scene": get_scene(device)}

@app.get("/device/{device}/brightness")
async def get_device_brightness(device):
    return {"brightness": get_brightness(device)}

@app.get("/device/{device}/effect")
async def get_device_effect(device):
    return {"effect": get_effect(device)}

@app.get("/device/{device}/effects")
async def get_device_effects(device):
    return {"effects": get_effects(device)}

@app.get("/device/{device}/palettes")
async def get_device_palettes(device):
    return {"palettes": get_palettes(device)}

@app.get("/device/{device}/palette")
async def get_device_palette(device):
    return {"palette": get_palette(device)}

@app.get("/device/{device}/speed")
async def get_device_speed(device):
    return {"speed": get_speed(device)}

@app.get("/device/{device}/intensity")
async def get_device_intensity(device):
    return {"intensity": get_intensity(device)}


if __name__ == "__main__":
    # Set up OpenRGB
    start_openrgb_server()

    uvicorn.run(app, host="127.0.0.1", port=8000)