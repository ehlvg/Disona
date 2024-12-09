import time
import requests

# Home Assistant details
HA_URL = "http://192.168.1.144:8123/api/services/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzMDI0NTQ4MzJlMDA0Mjg1OGRkMTgzMmU1MGEzNmQ5YiIsImlhdCI6MTczMzMyOTQ0NywiZXhwIjoyMDQ4Njg5NDQ3fQ.mOeh-Y5fw3x70ahb7hmOBXsIICybc3WSVfWjyc_mdgI"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# DMX entities
DMX_DEVICES = {
    "switch": ["switch.switch1", "switch.switch2"],  # On/Off switches
    "brightness": ["light.brightness_light1"],  # Brightness-only lights
    "color": ["light.lampa_1", "light.yndx_00544_osveshchenie"]  # Color and brightness lights
}


def toggle_switches(switches, delay=1, cycles=3):
    """Toggle switches on and off."""
    for _ in range(cycles):
        for switch in switches:
            # Turn on the switch
            requests.post(f"{HA_URL}switch/turn_on", headers=HEADERS, json={"entity_id": switch})
        time.sleep(delay)
        for switch in switches:
            # Turn off the switch
            requests.post(f"{HA_URL}switch/turn_off", headers=HEADERS, json={"entity_id": switch})
        time.sleep(delay)


def pulse_brightness(lights, steps=10, delay=0.1, min_brightness=50, max_brightness=255, cycles=3):
    """Pulse brightness-only lights."""
    for _ in range(cycles):
        # Gradually increase brightness
        for brightness in range(min_brightness, max_brightness, steps):
            for light in lights:
                requests.post(f"{HA_URL}light/turn_on", headers=HEADERS,
                              json={"entity_id": light, "brightness": brightness})
            time.sleep(delay)
        # Gradually decrease brightness
        for brightness in range(max_brightness, min_brightness, -steps):
            for light in lights:
                requests.post(f"{HA_URL}light/turn_on", headers=HEADERS,
                              json={"entity_id": light, "brightness": brightness})
            time.sleep(delay)


def pulse_color_and_brightness(lights, steps=10, delay=0.1, min_brightness=50, max_brightness=255, cycles=3):
    """Pulse brightness and cycle colors for color-capable lights."""
    colors = [
        [255, 0, 0],  # Red
        [0, 255, 0],  # Green
        [0, 0, 255],  # Blue
        [255, 255, 0],  # Yellow
        [255, 0, 255]  # Magenta
    ]

    for _ in range(cycles):
        for brightness in range(min_brightness, max_brightness, steps):
            for light in lights:
                color = colors[(brightness // steps) % len(colors)]
                requests.post(f"{HA_URL}light/turn_on", headers=HEADERS, json={
                    "entity_id": light,
                    "brightness": brightness,
                    "rgb_color": color
                })
            time.sleep(delay)
        for brightness in range(max_brightness, min_brightness, -steps):
            for light in lights:
                color = colors[(brightness // steps) % len(colors)]
                requests.post(f"{HA_URL}light/turn_on", headers=HEADERS, json={
                    "entity_id": light,
                    "brightness": brightness,
                    "rgb_color": color
                })
            time.sleep(delay)


if __name__ == "__main__":
    # Toggle switches (on/off)
    #toggle_switches(DMX_DEVICES["switch"], delay=1, cycles=3)

    # Pulse brightness for brightness-only lights
   # pulse_brightness(DMX_DEVICES["brightness"])

    # Pulse color and brightness for color-capable lights
    pulse_color_and_brightness(DMX_DEVICES["color"])