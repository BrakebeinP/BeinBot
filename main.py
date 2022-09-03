import os
from dotenv import load_dotenv
import json
import bein_bot
import discord

COGS = ['cogs.chat_cmd', 'cogs.utilities', 'cogs.twitter_stream']

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')


def get_prefix(bot, message):
    with open('json/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    try: 
        return prefixes[str(message.guild.id)]
    except KeyError:
        add_prefix(str(message.guild.id), os.getenv('BOT_PREFIX'))
        return prefixes[str(message.guild.id)]

def add_prefix(guild_id: str, prefix: str):
    with open('json/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[guild_id] = prefix

    with open('json/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)



if __name__ == '__main__':
    intents = discord.Intents.all()
    bein_bot = bein_bot.BeinBot(command_prefix=get_prefix, owner_id=int(os.getenv('BOT_OWNER_ID')), intents=intents)
    bein_bot.run(discord_token)
