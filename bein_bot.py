from discord.ext import commands
import discord
import discord.ext.commands.errors as command_errors

import os
from dotenv import load_dotenv
import sys

import logging
from random import choice
import json
from datetime import datetime, timezone

from main import COGS

load_dotenv()

d_logger = logging.getLogger('discord')
d_logger.setLevel(logging.DEBUG)
d_handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
d_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
d_logger.addHandler(d_handler)


class BeinBot(commands.Bot):

    def __init__(self, command_prefix, *, help_command=commands.DefaultHelpCommand(), tree_cls=discord.app_commands.tree.CommandTree, description=None, intents, **options):
        super().__init__(command_prefix, help_command=help_command, tree_cls=tree_cls, description=description, intents=intents, **options)
        self.log_channel = None
        self.allowed_mentions = discord.AllowedMentions(replied_user=False)


    async def on_ready(self):
        self.log_channel = self.get_channel(int(os.getenv('BOT_DEBUG_CHANNEL')))
        await self._log_channel('Bot started.')

        with open('json/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        with open ('json/cmd.json', 'r') as f:
            cmds = json.load(f)

        tw_rules = dict()

        for guild in self.guilds:
            if str(guild.id) not in prefixes.keys():
                self.add_prefix(str(guild.id), os.getenv('BOT_PREFIX'))
            if str(guild.id) not in cmds.keys():
                cmds[str(guild.id)] = dict()

            for channel in guild.channels:
                if channel.name.startswith(('tw-', 'twitter')) and isinstance(channel, discord.TextChannel):
                    if str(channel.topic) in tw_rules.keys():
                        tw_rules[str(channel.topic)].append(str(channel.id))
                    else:
                        tw_rules[str(channel.topic)] = [str(channel.id)]

        with open('json/cmd.json', 'w') as f:
            json.dump(cmds, f, indent=4)
        with open('json/twitter.json', 'w') as f:
            json.dump(tw_rules, f, indent=4)

        guilds = '\n - '.join([f'{guild.name}' for guild in self.guilds])
        print(f'{self.user.name} has connected to the following servers:\n - {guilds}')
        print(f'Default prefix = {os.getenv("BOT_PREFIX")}')

        for cog in COGS:
            await self.load_extension(cog)
            await self._log_channel(f'Loaded {cog}')
        
        with open('last_ctx.txt', 'r') as f:
            ch = self.get_channel(int(f.read()))
            await ch.send("I'M BAAAAAAAAAAAAAAAACK")



    async def on_guild_join(self, guild):
        with open('json/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        with open('json/cmd.json', 'r') as f:
            cmds = json.load(f)

        prefixes[str(guild.id)] = os.getenv("BOT_PREFIX")
        cmds[str(guild.id)] = dict()

        for channel in guild.channels:
            if channel.name.startswith(('tw-', 'twitter')) and isinstance(channel, discord.TextChannel):
                with open('json/twitter.json', 'r') as f:
                    tw_rules = json.load(f)

                if str(channel.topic) in tw_rules.keys():
                    n = max(tw_rules[str(channel.topic)].keys())+1
                    tw_rules[str(channel.topic)].append(str(channel.id))
                else:
                    tw_rules[str(channel.topic)] = [str(channel.id)]

                await self.reload_extension('cogs.twitter_stream')

        with open('json/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        with open('json/cmd.json', 'w') as f:
            json.dump(cmds, f, indent=4)


    async def on_error(self, event, *args, **kwargs):
        with open('logs/err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
                print(args)
            elif event == 'command_error':
                f.write(f'ERROR: {args[0]}\n')
            else:
                await self._log_channel(f'ERROR: ```{sys.exc_info()}\n{event}\n{args}\n{kwargs}```')
    

    async def on_command_error(self, ctx, error):
        if isinstance(error, command_errors.CheckFailure):
            if isinstance(error, command_errors.NotOwner):
                await ctx.message.add_reaction('🚫')
                await ctx.reply('You are not the bot owner')
            else:
                err_msgs = [
                    'You must construct additional pylons.',
                    'Your power level is below 9000.',
                    'Nice try, idiot.',
                    'Dick not big enough.'
                ]

                await ctx.send(choice(err_msgs) + f'\n ({error})')

        if isinstance(error, command_errors.MissingRequiredArgument):
            await ctx.send('You accidentally the command argument.')

        if isinstance(error, command_errors.CommandNotFound):
            with open('json/cmd.json', 'r') as f:
                commands = json.load(f)

            try:
                cmd = commands[str(ctx.guild.id)][str(ctx.message.content[1:])]['response']
                await ctx.reply(cmd)
                #TODO: get emoji responses working for guilds that the bot is not in
            except KeyError:
                await ctx.reply('Command not found')


    async def on_message(self, msg):
        if msg.author == self.user:
            return

        if '69' in msg.content.split(' '):
            await msg.channel.reply('Nice.')

        await self.process_commands(msg)

    
    async def on_command(self, ctx):
        await self._log_channel(f'{ctx.command} invoked by {ctx.author}')


    async def on_guild_channel_update(self, before, after):
        if isinstance(before, discord.TextChannel):
            tw_cog = self.get_cog('TwitterStream')
            if before.topic != after.topic and before.name == after.name:
                if before.name in ('tw-', 'twitter-'):
                    with open('json/twitter.json', 'r') as f:
                        tw_rules = json.load(f)

                    if before.topic in tw_rules.keys() and len(tw_rules[before.topic])==1:
                        del(tw_rules[before.topic])
                        await tw_cog._del_rule(before.topic)

                    if after.topic in tw_rules.keys():
                        tw_rules[after.topic].append(str(after.id))
                    else:
                        tw_rules[after.topic] = [str(after.id)]
                        await tw_cog._add_rule(after.topic)

                    with open('json/twitter.json', 'w') as f:
                        json.dump(tw_rules, f, indent=4)


    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, discord.TextChannel):
            tw_cog = self.get_cog('TwitterStream')
            if channel.name.startswith(('tw-', 'twitter')):
                with open('json/twitter.json', 'r') as f:
                    tw_rules = json.load(f)

                if channel.topic in tw_rules.keys():
                    if len(tw_rules[str(channel.topic)]) > 1:
                        for v in tw_rules[str(channel.topic)].values():
                            if v == str(channel.id):
                                del(tw_rules[str(channel.topic)][v])     
                    else:
                        del(tw_rules[str(channel.topic)])
                        await tw_cog._del_rule(channel.topic)

                with open('json/twitter.json', 'w') as f:
                    json.dump(tw_rules, f, indent=4)

                
    async def _log_channel(self, msg):
        now = datetime.now(timezone.utc)
        frame = sys._getframe(1)
        called_func = frame.f_code.co_name
        mod = frame.f_code.co_filename.split('\\')[-1][:-3]
        m = await self.log_channel.send(f'`{now}:{mod}:{called_func}`: {msg}')
        return m
