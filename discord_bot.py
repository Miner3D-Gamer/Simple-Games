import discord
from discord.ext import commands
import os

# Intents are required to handle reactions properly
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

from discord_engine import handle_raw_reaction, handle_message


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    r = await handle_raw_reaction(payload, bot)
    if isinstance(r, Exception):
        print(r)
        return
    if r:
        return
    # Here goes your code
    pass


@bot.event
async def on_message(message: discord.Message):
    r = await handle_message(message, bot)
    if isinstance(r, Exception):
        print(r)
        return
    if r or r is None:
        return
    # Here goes your code
    pass


token_file = os.path.join(os.path.dirname(__file__), "bot.token")

with open(token_file, "r") as f:
    bot.run(f.read())
