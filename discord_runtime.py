from typing import Optional, Union, Literal, Dict, TypedDict, List
import framework
import discord_emoji
import discord

# Dictionary to store messages by their IDs


class FrameworkDict(TypedDict):
    framework: framework.Framework
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


message_store: Dict[int, FrameworkDict] = EasyDict()

from string import ascii_lowercase


async def get_message(
    channel_id: int, message_id: int, bot: discord.bot.Bot
) -> Optional[discord.Message]:
    channel = bot.get_channel(channel_id)
    if channel is None:
        print(f"Channel {channel_id} not found.")
        return None
    return await channel.fetch_message(message_id)  # type: ignore


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


def convert_special(reaction):
    ################################ THIS IS NOT GUD BUT THE BEST I CAN DO FOR KEYBOARD ONLY KEYS
    conversion = {"BACKSPACE": "arrow_backward", " ": "blue_square", "-": "no_entry"}

    if reaction in conversion:
        return conversion[reaction]

    for key, value in conversion.items():
        if value == reaction:
            return key
    return reaction


def convert_reaction_to_send(reaction: str) -> str:
    if reaction in ascii_lowercase:
        return letter_to_regional_indicator(reaction)
    elif reaction.isdigit():
        return int_to_text(int(reaction))

    return convert_special(reaction)


def convert_reaction_to_process(reaction: str) -> str:
    r = regional_indicator_to_letter(reaction.strip(":")).lower()
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
        s = convert_special(e)
        if s != e:
            return s
    return r


async def remove_reactions(
    message: discord.Message, allowed_reactions: List[str], bot: discord.bot.Bot
):
    previoud_reactions = message.reactions[::-1]
    allowed_reactions = allowed_reactions[::-1]
    final = []
    blacklist = []

    # THIS CODE DOES WORK :D or does it?
    for reaction_idx in range(len(previoud_reactions)):
        if previoud_reactions[reaction_idx].emoji == allowed_reactions[reaction_idx]:
            blacklist.append(previoud_reactions[reaction_idx])
        else:
            break
    final = previoud_reactions[::-1][: len(blacklist)]

    for reaction in final:
        await message.remove_reaction(reaction.emoji, bot.user)  # type: ignore
    return blacklist


async def change_reactions(
    message: discord.Message,
    reactions: List[
        Union[discord.PartialEmoji, str]
    ],
    bot: discord.bot.Bot,
):
    final_reactions = []
    for r in reactions:
        if isinstance(r, str):
            r = convert_reaction_to_send(r)
            r = get_emoji(r)
        final_reactions.append(r)

    blacklist = await remove_reactions(message, final_reactions, bot)
    final_reactions = final_reactions[len(blacklist) :]

    for r in final_reactions:

        try:
            await message.add_reaction(r)
        except discord.errors.HTTPException:
            print(f"Failed to add reaction '{r}' to message {message.id}")


__all__ = ["handle_raw_reaction", "handle_message", "stop_bot"]


async def stop_bot(bot: discord.bot.Bot):
    await bot.close()


async def handle_message(
    message: discord.Message, bot: discord.bot.Bot
) -> Optional[Union[bool, Exception]]:
    if message.author == bot.user:
        return False

    if not message.content.startswith("!"):
        return None
    content = message.content[1:]

    if content.startswith("start"):
        args = content.split()[1:]
        if len(args) > 1:
            await message.channel.send("Please provide only one argument.")
            return True
        framework_instance = framework.Framework("discord")

        if len(args) == 1:
            valid = framework.is_valid_game_id(args[0])
            if valid:
                framework_instance.select_game(args[0], "discord")

                send = await message.channel.send(f"Selected: {args[0]}")

                message_store[send.id]["framework"] = framework_instance
                message_store[send.id]["ready"] = False

                await change_reactions(send, framework_instance.accepted_inputs, bot)  # type: ignore
                message_store[send.id]["ready"] = True

                return True
        else:
            args = [""]

        selected = framework_instance.select_game_from_user(
            message.author.name, args[0]
        )
        if isinstance(selected, framework.SelectedGame):
            send = await message.channel.send(f"Selected: {args[0]}")

            message_store[send.id]["framework"] = framework_instance
            message_store[send.id]["ready"] = False

            await change_reactions(send, framework_instance.accepted_inputs, bot)  # type: ignore
            message_store[send.id]["ready"] = True
        else:
            if isinstance(selected, Exception):
                selected = "Error:\n" + "\n".join(selected.args)

            send = await message.channel.send(selected)
        return True
    return None


def get_username(member: discord.Member) -> str:
    if member.nick is not None:
        return member.nick
    return member.name


async def handle_raw_reaction(
    payload: discord.RawReactionActionEvent, bot: discord.bot.Bot
) -> Optional[Union[bool, Exception]]:

    # Definitely not for our purposes
    if payload.user_id == bot.user.id:  # type: ignore
        return False

    message = await get_message(payload.channel_id, payload.message_id, bot)
    # Message not found
    if message is None:
        return None

    if message.author.id != bot.user.id:  # type: ignore
        return None

    await message.remove_reaction(payload.emoji, payload.member)  # type: ignore

    if payload.message_id in message_store:
        if not message_store[payload.message_id]["ready"]:
            return True

        framework_instance = message_store[payload.message_id]["framework"]
        reaction_str = convert_reaction_to_process(payload.emoji.name)  # type: ignore

        output = framework_instance.run_game(reaction_str, {"user_id": payload.user_id, "username": get_username(payload.member)})  # type: ignore

        # Game asked framework to change reactions
        if isinstance(output, framework.ChangeInputs):
            await change_reactions(message, output.inputs, bot)  # type: ignore
            output = output.frame

        # Frame remains the same
        if output is None:
            return True
        # Error occured
        if isinstance(output, Exception):
            await message.edit(content=str(output))
            return True
        # Game asked framework to stop
        if isinstance(output, framework.StopFramework):
            await message.edit(content=output.last_frame)
            message_store.pop(payload.message_id)
            return True
        # Game asked framework to send new frame
        if isinstance(output, str):
            # output = output.replace(" ", "ㅤ")
            output = "```%s```" % output
            await message.edit(content=output)
            return True
        # ???
        return Exception(f"Unknown output: {output}")

    else:
        return None


# This framework is pretty well written, or is it?
#                        .-=+*###%@@@@@@@@@@%#*=-.
#                        @@@@#*+#-.      .::*#@@@@@*
#                .+#@@@@@*.  .::--=--=-..:..     .@@@@@*=:
#              -*@@@@:   -***#*##########%*++===.     #@@@#:
#        .--==#@@+  :*%@@@@@@@@@%@@%%@@@%@#*#%##*+++:    %@@*:
#        =%@@@@:  #@@@%%%%%@%%%%%%%%@%%%@@@%%%%%%%%##*+.   @@@#.
#     =-+#@@%:  #%@%######%%%%%%#%%%%%@%%%%#%%%%%%%%@%#*=    @@@*
#     %%@@@: .#@%%#####%%%%%##%#%#####################%@%%+    @@*
#     @@@=..%@@%###########################%%#%#%#######%%%%+   *@#=
#     @@* :%%%################%%##%%%%%#############*###*#%@%#-  #@@*
#  =+%@# -%%#**######%%#####**##***+******#########*#******#%%#=: :@%
# -%%@@ -%%##*****##%#%%%%%%%%##%%%%%%%###%%%%##**##****#####%%*-. @@#
# -%@@ :%%#**#######****####*##########%%%########*#####****##%#*-. @@#=
# -%@: ##*####**++****##**##**++++++*+++++++++*********#####*###*-:  @@%*-
# -@@.=%****##*#*#*#######***%%%%%%##%%#%%##########*#####*****##*=- +@@%=
# -@@ #%#*****####*********###*##########*#####****#*####******##+== -@@*
# -@= ###*##*+*********###*********+*++++++****##**#####**#**####+-=: @@
# -@* #*+**#########################%%%%@%%###***####**###**#***#++=. @@*
# -@..#*++*****#***##%%###*****+***#*##***##****#**+********#***#+=-- @@#
# -@ .#*++++*+*+=*********#######*#*#**###############**********#*+=: @@%
# -@ =%++##%%%%%%%%%#*#**####*##########*#####%%%###%#%%#***#***###-: *@%-
# =@.*#+#%%%%%%%#%%%%%%#%###**#***++*####%%##%##%%%%%%%%%%%#*****#%=. +@@-
# *@ %##@#----::--:::-++*++****+*###+*==-:-:-::=::: .:-.=*%%#*****%=: *@@=
# %# %#%.                .-=+**+**=+=-::             ..    .*#*###%*- -@@#+-.
# %@ %%%::-*#%%#=--:       :-==++***+==---+*+:....:-+*##%%#*#%#*=-.   %@@@@@-
# @@:*   .-=-::-@@#%@%#**+==++%@@@%*=-.:+*+:.=%%#*#= .--.  .+#%%%%@@@@@+***@=
# @    @@%*:  .%*    -=::--. ...   . -*-+=:-#@*= :%@@   -**    @@@@@+:=*%=.@+
# @+  @@+==:--+%#....::   .=-  ***= +%+:- . .- :  .+#++-:-%%   +*:-  +##=  @=
# @++ +@= .=+*++*###*=-=+++%  @@@@@ -%+=-##+=+#%%%%*++=**+%% :%#+=#-+%##=.-@=
# @=++ @#=-+#*-:    .-=-:+%% +%%##%% *@#-.:==-...:::=+#%%#%* #%***%::-*@=:%@-
# %*.@ @@#+=+*##*+==--=##%% =######%@ +##%#=-----=+**++++*@  %#++*#.+:-#%-@@-
# %+-*%  *@@%##%##%@@@@@*. =%**#%##*#% .%@@%%@@%######%%@@  *%****+:@#====@@-
# #=* %%#=:. .. ...      :##*+#%@#*=+%%=    ..::.:::.... :#%%#++*#- @*==-@@%-
# *@% +*+*##***######**=*%#**+*##++*+*#@%#***##**###%%%#%%#**++++#-.%%#*=@@%-
# =@@ :*=++*####*+=--=***++*######*##++++++*+==+++**+*******++++*#-.%%=.%%*-
# -%@# #++=+**==-=+#@%=+%%######%%%#*+#@@%--#%%*++=+*+**********#+ -#*=@@+
# -%@: ++==++++*#%%#=. *@#%#%%%###%%*###%%=- .+%%#*++++**=+*****#- -*=%@%=
# -%@@- -++++++*++-.  .==+##******#%#*##****+  .=****+++*#*******:  :=@@%+
#  -+@@@.++++====-. .+###  .===---:.--:.-+*#%**. .+#**+===+++*##+ %@@@*=-.
#     @@ *=++++=-.:+%%%#+==:...:+#%#=.:.+*#*%##%%-.-=++*====+*#+= +@@+
#     @@ *+++++=-=+*++---==-=::+-    .===+=+#%+==%#+===+*****=-:: @@%:
#     @@ +*++++***+++===:.. ::+-.:--::=: :--===:::+%##*+*=:-++-:  @@%:
#     @@  --+#**+:   ..::.:.. ..      .. =**=-:-:: -*##*-.:::==- *@@%
#     @@@  -:=#*:::::-+#%#++=--::::-++%%#@-# .  .::.-##*- -==-: -@@%%-
#     @@@  ::=#+::-=-.   :-+++@@@@@@%=@: .   .:..-:-=#%#. -+*=. @@*--.
#     %%@@  .-%#===..-=-                 :*##%%%+=:=%%%*:.-+-  *@#
#     :*@@*  :%%==::=*%%###*-=:.::..:-=#%%#**###=--:=-:::-==:  @@=
#        @@  .-=:::-+#****##%%%%##%#####*+****##+::.:-:::.:-  @@@=
#        #@@  :----=++=--+=-==+****++=++*%+=*##-:--.=%:.::-.  @@%=
#        -@@%  -:--..==*=-....::-=--..:  :**#*:.-==-==:::-. =@@+-
#        :@@@@ .:::-=*#+=-::.:-:.  ...::--*#**:::.-:::--:  .@@
#         *#@@   :---*###*==--..  .:.:*#***+=+--::--::::. -@@=
#          -#@@#  ::-:-=*#%#*+=++=#**==*%%+=------=::::   %@@:
#            *@@+  .::--:-==***==++**%#-==+=:-------:   .@@+-
#            .+@@@   .-+-+*+--+***-*=-#=-*=:-=---:     @@@
#              .#@@=  .-::-*+==+=+=+=-++-.--:=::    %@@@+
#                +@@@   :: :--=*+=+=+=-*=---:    @@@@%
#                :#@@@:   :=:.--..-::::.=-.   #@@@@%+.
#                    @@@:       ...:: .     @@@@
#                    +@@@@@@             @@@@@
#                     ==-=#@@@@@@@@@@@@@@@
# (Squint eyes for easier ascii recognition)
