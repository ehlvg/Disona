import base64
import discord  # pip install discord.py
import requests  # pip install requests
import logging  # Logging for debug
import re
import random
import google.generativeai as genai
import toml  # To load the configuration
from PIL import Image

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the configuration from the toml file
config = toml.load('config.toml')

# General configuration
ALLOWED_CHANNELS = config['general']['allowed_channels']
BOT_ALIASES = config['general']['bot_aliases']
EIGHT_BALL_ANSWERS = config['eight_ball_answers']['answers']

# API Keys
OWM_API_KEY = config['api_keys']['owm_api_key']
GENAI_API_KEY = config['api_keys']['genai_api_key']
DISCORD_API_KEY = config['api_keys']['discord_api_key']
genai.configure(api_key=GENAI_API_KEY)

# System prompts
normal_system_prompt = config['system_prompts']['normal_system_prompt']
photo_system_prompt = config['system_prompts']['photo_system_prompt']
dice_8ball_system_prompt = config['system_prompts']['dice_8ball_system_prompt']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.debug(f"Bot logged in as {client.user}")
    print(f"Bot is online as {client.user}")

@client.event
async def on_message(message):
    logger.debug(f"Received message from {message.author}: {message.content}")

    # Ignore messages from the bot itself
    if message.author == client.user:
        logger.debug("Message is from the bot itself, ignoring.")
        return

    # Check if it's a DM or an allowed channel
    if isinstance(message.channel, discord.DMChannel):
        # Handle DM messages directly
        logger.debug("Message is from a DM channel.")
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image"):
                    image = await attachment.read()
                    photo_model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=photo_system_prompt)
                    response = photo_model.generate_content([{'mime_type': 'image/jpeg', 'data': base64.b64encode(image).decode('utf-8')}, message.content])
                    await message.channel.send(response.text)
                    return
        # Proceed with other normal message handling in DMs
        user_prompt = f"User just said: '{message.content}'. Respond in character."
        system_prompt = normal_system_prompt

    elif message.channel.name in ALLOWED_CHANNELS:
        # If it's from an allowed channel, continue processing
        pass
    else:
        logger.debug(f"Channel '{message.channel.name}' is not allowed, ignoring.")
        return

    # Check for bot mentions in allowed channels
    bot_mentioned = client.user in message.mentions
    indirect_bot_mention = any(alias in message.content.lower() for alias in BOT_ALIASES)

    # Bot should only respond if it's mentioned directly or if there's an indirect mention
    if not bot_mentioned and not indirect_bot_mention:
        logger.debug("Bot was not mentioned or no indirect mention in allowed channel, ignoring.")
        return

    # Handle normal user input in allowed channels
    content = message.content.lower()

    # Checking for various types of requests
    dice_match = re.search(r'roll\s+(\d+)d(\d+)', content)
    weather_match = re.search(r"weather in ([a-zA-Z\s\-]+)", content)
    eight_ball_match = re.search(r'8-ball', content)

    if dice_match:
        dice_count = int(dice_match.group(1))
        dice_sides = int(dice_match.group(2))
        # Add a check to ensure the roll is not too big
        if dice_count > 100 or dice_sides > 100:  # Added check
            user_prompt = f"The user asked to roll {dice_count}d{dice_sides}. Can't make this a roll this big."
            system_prompt = dice_8ball_system_prompt
        else:
            rolls = [random.randint(1, dice_sides) for _ in range(dice_count)]
            rolls_str = ", ".join(str(r) for r in rolls)
            user_prompt = f"The user asked to roll {dice_count}d{dice_sides}. The result is {rolls_str}."
            system_prompt = dice_8ball_system_prompt

    elif eight_ball_match:
        # Magic 8-ball
        answer = random.choice(EIGHT_BALL_ANSWERS)
        user_prompt = f"The user asked the 8-ball. The chosen answer is '{answer}'."
        system_prompt = dice_8ball_system_prompt

    elif weather_match:
        # Weather forecast
        city = weather_match.group(1).strip()
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric"
        w_response = requests.get(weather_url)
        if w_response.status_code == 200:
            w_json = w_response.json()
            temp = w_json['main']['temp']
            description = w_json['weather'][0]['description']
            user_prompt = f"The user asked about the weather in {city}. The temperature is {temp}°C and it's {description}."
            system_prompt = normal_system_prompt
        else:
            user_prompt = "The user asked about the weather, but I couldn't get the data."
            system_prompt = normal_system_prompt

    else:
        # Normal conversation
        user_prompt = f"User just said: '{message.content}'. Respond in character."
        system_prompt = normal_system_prompt

    logger.debug(f"Prepared user prompt: {user_prompt}")

    # Request to the generative model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_prompt)
    response = model.generate_content(user_prompt)

    try:
        ai_reply = response.text
        logger.debug(f"Extracted AI reply: {ai_reply}")
    except (KeyError, IndexError) as e:
        logger.debug(f"Error extracting AI reply: {e}")
        ai_reply = "something went wrong"

    await message.channel.send(ai_reply)
    logger.debug("Sent reply back to Discord.")

def start_bot():
    client.run(DISCORD_API_KEY)