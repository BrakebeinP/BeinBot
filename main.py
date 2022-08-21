import os
import logging
from discord.ext import commands
from dotenv import load_dotenv
from random import choice
import json

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    try: 
        return prefixes[str(message.guild.id)]
    except KeyError:
        add_prefix(str(message.guild.id), os.getenv('BOT_PREFIX'))
        return prefixes[str(message.guild.id)]

def add_prefix(guild_id: str, prefix: str):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[guild_id] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

bot = commands.Bot(command_prefix=get_prefix, owner_id=int(os.getenv('BOT_OWNER_ID')))

cog_files = ['cogs.chat_cmd', 'cogs.utilities']

for cog_file in cog_files:
    bot.load_extension(cog_file)
    print(f'Loaded {cog_file}')


@bot.event
async def on_ready():
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    for guild in bot.guilds:
        if str(guild.id) not in prefixes.keys():
            add_prefix(str(guild.id), os.getenv('BOT_PREFIX'))
    guilds = '\n - '.join([f'{guild.name}' for guild in bot.guilds])
    print(f'{bot.user.name} has connected to the following servers:\n - {guilds}')
    print(f'Default prefix = {os.getenv("BOT_PREFIX")}')
    print(';'.join([ch.name for ch in guild.channels for guild in bot.guilds]))

@bot.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = os.getenv("BOT_PREFIX")

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        elif event == 'command_error':
            f.write(f'ERROR: {args[0]}\n')
        else:
            raise

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        if isinstance(error, commands.NotOwner):
            await ctx.message.add_reaction('🚫')
            await ctx.reply('You are not the bot owner', mention_author=False)
        else:
            err_msgs = [
                'You must construct additional pylons.',
                'Your power level is below 9000.',
                'Nice try, idiot.',
                'Dick not big enough.'
            ]
            await ctx.send(choice(err_msgs) + f'\n ({error})')

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You accidentally the command argument.')

    if isinstance(error, commands.CommandNotFound):
        with open('commands.json', 'r') as f:
            commands = json.load(f)
            print(ctx.message)
        try:
            cmd = commands[str(ctx.guild.id)]
            print(cmd)
        except:
            ctx.reply('Command not found', mention_author=False)


@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    if '69' in msg.content.split(' '):
        await msg.channel.reply('Nice.', mention_author=False)

    await bot.process_commands(msg)


if __name__ == '__main__':
    bot.run(token)
