import discord
from discord.ext import commands
import os

import discord_emoji

import engine
from typing import Optional, Union, Literal, Dict, TypedDict, List

# Intents are required to handle reactions properly
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

assert isinstance(bot, commands.bot.Bot)

# Dictionary to store messages by their IDs


class EngineDict(TypedDict):
    engine: engine.Engine
    ready: bool


class EasyDict(dict):
    def __init__(self, *args, **kwargs):
        self.__dict__ = self
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            self.__dict__[key] = {}
            return self.__dict__[key]


message_store: Dict[int, EngineDict] = EasyDict()

from string import ascii_lowercase


def letter_to_regional_indicator(letter: str) -> str:
    """
    Converts a single letter (A-Z or a-z) to its corresponding regional indicator emoji.
    """
    if len(letter) != 1 or not letter.isalpha():
        return letter

    # Convert to uppercase since regional indicators are based on capital letters
    return chr(ord(letter.upper()) + 0x1F1E6 - ord("A"))


def regional_indicator_to_letter(regional_indicator: str) -> str:
    """
    Converts a regional indicator emoji back to its corresponding letter.
    """
    if len(regional_indicator) != 1 or not (
        0x1F1E6 <= ord(regional_indicator) <= 0x1F1FF
    ):
        return regional_indicator

    return chr(ord(regional_indicator) - 0x1F1E6 + ord("A"))


def get_emoji(reaction: str) -> str:
    r = discord_emoji.to_unicode(reaction)
    return reaction if r is None else r


def int_to_text(reaction: int) -> str:
    l = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    return l[reaction]


def text_to_int(reaction: str) -> Union[int, str]:
    l = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    if reaction in l:
        return l.index(reaction)
    return reaction


def convert_reaction_to_send(reaction: str) -> str:
    if reaction in ascii_lowercase:
        return letter_to_regional_indicator(reaction)
    elif reaction.isdigit():
        return int_to_text(int(reaction))
    return reaction


def convert_reaction_to_process(reaction: str) -> str:
    r = letter_to_regional_indicator(reaction)
    e = discord_emoji.to_discord(r, get_all=True, put_colons=False)
    if isinstance(e, list):
        if len(e) == 0:
            return r
        e = e[0]
    if e is not None:
        n = text_to_int(e)
        if isinstance(n, int):
            if n != -1:
                return str(n)
    return r


async def remove_reactions(message: discord.Message):
    previoud_reactions = message.reactions
    for reaction in previoud_reactions:
        await message.remove_reaction(reaction.emoji, bot.user)  # type: ignore


async def change_reactions(
    message: discord.Message,
    reactions: List[
        Union[discord.GuildEmoji, discord.AppEmoji, discord.PartialEmoji, str]
    ],
):
    await remove_reactions(message)

    for r in reactions:

        if isinstance(r, str):
            if r == " ":
                r = "blue_square"
            else:
                r = convert_reaction_to_send(r)
            r = get_emoji(r)
        try:
            await message.add_reaction(r)
        except discord.errors.HTTPException:
            print(f"Failed to add reaction '{r}' to message {message.id}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")


async def get_message(channel_id: int, message_id: int) -> Optional[discord.Message]:
    channel = bot.get_channel(channel_id)
    if channel is None:
        print(f"Channel {channel_id} not found.")
        return None
    return await channel.fetch_message(message_id)  # type: ignore


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:  # type: ignore
        return

    message = await get_message(payload.channel_id, payload.message_id)
    if message is None:
        return

    if message.author.id != bot.user.id:  # type: ignore
        return

    await message.remove_reaction(payload.emoji, payload.member)  # type: ignore

    if payload.message_id in message_store:
        if not message_store[payload.message_id]["ready"]:
            return

        engine_instance = message_store[payload.message_id]["engine"]
        reaction_str = convert_reaction_to_process(payload.emoji.name)  # type: ignore

        output = engine_instance.run_game(reaction_str, payload.user_id, payload.member.name)  # type: ignore

        # Game asked engine to change reactions
        if isinstance(output, engine.ChangeInputs):
            await change_reactions(message, output.inputs)  # type: ignore
            output = output.frame

        # Frame remains the same
        if output is None:
            return
        # Error occured
        if isinstance(output, Exception):
            await message.edit(content=str(output))
            return
        # Game asked engine to stop
        if isinstance(output, engine.StopEngine):
            await message.edit(content=output.last_frame)
            message_store.pop(payload.message_id)
            return
        # Game asked engine to send new frame
        if isinstance(output, str):
            # output = output.replace(" ", "ㅤ")
            output = "```%s```" % output
            await message.edit(content=output)
            return
        # ???
        raise Exception(f"Unknown output: {output}")

    else:
        print(
            f"Received reaction from {payload.user_id} with no engine: {payload.emoji}"
        )


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    print(f"Received message from {message.author}: {message.content}")
    if not message.content.startswith("!"):
        return
    content = message.content[1:]

    if content == "stop":
        await stop_bot()
    if content.startswith("start"):
        args = content.split()[1:]
        if len(args) > 1:
            await message.channel.send("Please provide only one argument.")
            return
        engine_instance = engine.Engine()

        if len(args) == 1:
            valid = engine.is_valid_game_id(args[0])
            if valid:
                engine_instance.select_game(args[0])

                send = await message.channel.send(f"Selected: {args[0]}")

                message_store[send.id]["engine"] = engine_instance
                message_store[send.id]["ready"] = False

                await change_reactions(send, engine_instance.accepted_inputs)  # type: ignore
                message_store[send.id]["ready"] = True

                return
        else:
            args = [""]

        selected = engine_instance.select_game_from_user(message.author.name, args[0])
        if isinstance(selected, engine.SelectedGame):
            send = await message.channel.send(f"Selected: {args[0]}")

            message_store[send.id]["engine"] = engine_instance
            message_store[send.id]["ready"] = False

            await change_reactions(send, engine_instance.accepted_inputs)  # type: ignore
            message_store[send.id]["ready"] = True
        else:
            if isinstance(selected, Exception):
                selected = "Error:\n" + "\n".join(selected.args)

            send = await message.channel.send(selected)

            # if not isinstance(selected, Exception):
            #     message_store[send.id] = engine


async def stop_bot():
    await bot.close()


token_file = os.path.join(os.path.dirname(__file__), "bot.token")

with open(token_file, "r") as f:
    bot.run(f.read())
