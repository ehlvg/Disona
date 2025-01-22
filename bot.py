import base64
import discord
import logging
import google.generativeai as genai
import toml
import random
from google.generativeai.types import CallableFunctionDeclaration  # Импортируем правильный класс

# Настройка базового логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Загрузка конфигурации из toml файла
config = toml.load('/Users/daniil/Watches/pythonProject/config.toml')


ALLOWED_CHANNELS = config['general']['allowed_channels']
BOT_ALIASES = config['general']['bot_aliases']
INDERECT_MENTION_CHANNELS = config['general']['indirect_bot_mention_channels']

# API ключи
GENAI_API_KEY = config['api_keys']['genai_api_key']
DISCORD_API_KEY = config['api_keys']['discord_api_key']
genai.configure(api_key=GENAI_API_KEY)

# Системные подсказки
model_system_prompt = config['system_prompts']['system_prompt']

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

    # Игнорируем сообщения от самого бота
    if message.author == client.user:
        logger.debug("Message is from the bot itself, ignoring.")
        return

    # Инициализируем user_prompt значением по умолчанию
    user_prompt = ""

    # Проверяем, является ли сообщение личным или из разрешенного канала
    if isinstance(message.channel, discord.DMChannel):
        logger.debug("Message is from a DM channel.")
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image"):
                    # Обработка изображения
                    image_data = await attachment.read()
                    encoded_image = base64.b64encode(image_data).decode('utf-8')
                    photo_model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=model_system_prompt
                    )
                    response = photo_model.generate_content(
                        user_prompt=message.content,
                        media_inputs=[
                            {'mime_type': attachment.content_type, 'data': encoded_image}
                        ]
                    )
                    await message.channel.send(response.text)
                    return
        user_prompt = f"User just said: '{message.content}'. Respond in character."
    else:
        # Check if the message is from an allowed channel or mentions the bot
        if message.channel.name in ALLOWED_CHANNELS or \
                (message.mentions and client.user in message.mentions) or \
                any(alias.lower() in message.content.lower() for alias in BOT_ALIASES) or \
                (message.channel.name in INDERECT_MENTION_CHANNELS):
            logger.debug(
                f"Message from allowed channel '{message.channel.name}', mentions the bot, or contains bot alias.")
        else:
            logger.debug(f"Channel '{message.channel.name}' is not allowed, ignoring.")
            return

        user_prompt = f"User just said: '{message.content}'. Respond in character."

    # Далее продолжаем обработку сообщения
    def roll_dice(dice_count: int, dice_sides: int):
        """Бросает указанное количество костей с указанным количеством граней."""
        rolls = [random.randint(1, dice_sides) for _ in range(dice_count)]
        logger.debug("Rolled " + str(rolls))
        return rolls

    # Инструменты для модели
    functions = {
        "roll_dice": roll_dice
    }

    # Проверка на команды, например, roll dice
    if "roll dice" in message.content.lower():
        # Извлекаем количество костей и количество граней
        try:
            params = message.content.split(" ")[2:]  # assuming "roll dice X Y"
            dice_count = int(params[0])
            dice_sides = int(params[1])
            rolls = roll_dice(dice_count, dice_sides)
            await message.channel.send(f"Rolled dice: {', '.join(map(str, rolls))}")
        except Exception as e:
            await message.channel.send("Error rolling dice. Please use the format: 'roll dice <count> <sides>'")
            logger.error(f"Error rolling dice: {e}")
        return

    # Создаем модель с инструментами
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=model_system_prompt,
        tools=[CallableFunctionDeclaration(name="roll_dice", function=roll_dice, description="Rolls a specified number of dice with a specified number of sides")]
    )

    # Генерация контента от модели
    try:
        response = model.generate_content(user_prompt)
        logger.debug(f"Model response: {response}")

        # Check the structure of the response object before accessing text
        if hasattr(response, 'text'):
            ai_reply = response.text
        else:
            ai_reply = "Error: Model response does not have 'text' attribute."

        logger.debug(f"Extracted AI reply: {ai_reply}")
    except (KeyError, IndexError) as e:
        logger.debug(f"Error extracting AI reply: {e}")
        ai_reply = "Something went wrong."

    await message.channel.send(ai_reply)
    logger.debug("Sent reply back to Discord.")

def start_bot():
    client.run(DISCORD_API_KEY)