import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from random import choice

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', owner_id=int(os.getenv('BOT_OWNER_ID')))

cog_files = ['cogs.chat_cmd', 'cogs.utilities']

for cog_file in cog_files:
    bot.load_extension(cog_file)
    print(f'Loaded {cog_file}')

@bot.event
async def on_ready():
    guilds = '\n - '.join([f'{guild.name}, Owner: {guild.owner_id}' for guild in bot.guilds])
    print(f'{bot.user.name} has connected to the following servers:\n - {guilds}')
    print(f'Command prefix = {bot.command_prefix}')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        if isinstance(error, commands.errors.NotOwner):
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
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('You accidentally the command argument.')
    


@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    if '69' in msg.content.split(' '):
        await msg.channel.reply('Nice.', mention_author=False)

    await bot.process_commands(msg)


if __name__ == '__main__':
    bot.run(token)
