import asyncio
from pyartnet import ArtNetNode

# Art-Net DMX Node Configuration
ARTNET_IP = "192.168.1.23"  # Replace with your Art-Net node's IP address
UNIVERSE = 0  # DMX Universe to control
CHANNELS = {
    "switch": [1],  # Channels for on/off switches
    "brightness": [2],  # Channels for brightness-only lights
    "color": [3]  # Starting channel for RGB lights (Red, Green, Blue)
}

async def main():
    # Initialize Art-Net Node
    node = ArtNetNode(ARTNET_IP, port=6454)

    # Add a universe
    universe = node.add_universe(UNIVERSE)

    # Outputs for each type of device
    switch_outputs = [universe.add_channel(ch, 1) for ch in CHANNELS["switch"]]
    brightness_outputs = [universe.add_channel(ch, 1) for ch in CHANNELS["brightness"]]
    # For RGB, use a single channel group with width 3
    color_output = universe.add_channel(CHANNELS["color"][0], 3)

    # Example: Set color to red and full brightness for RGB light
    await color_output.add_fade([255, 0, 0], 1000)  # Gradually set to red over 1 second

    await asyncio.sleep(2)  # Keep the node running for 2 seconds as an example

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to start the event loop