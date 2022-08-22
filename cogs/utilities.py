import discord
import asyncpraw
import os
from discord.ext import commands
from dotenv import load_dotenv
import urllib.request
import shutil
from . import helper_funcs as hf
import json
import sys

load_dotenv()

reddit = asyncpraw.Reddit(
    client_id = os.getenv('REDDIT_CLIENT_ID'),
    client_secret = os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='BeinBot v0.0.1 by /u/BrakebeinP'
)



class ChatUtilities(commands.Cog, name='Utilities'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='createchannel')
    @commands.has_permissions(manage_channels=True)
    async def create_channel(self, ctx, channel_name='kek'):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating new channel: {channel_name} in {guild.name}')
            await guild.create_text_channel(channel_name)


    @commands.command(name='reddit', help='Reddit vid/img downloader')
    async def reddit_media(self, ctx, cmd_url: str):
        ctx.embed = '[]'
        s = await reddit.submission(url=cmd_url)
        if s.is_video:
            vid_h = s.media['reddit_video']['height']
            vid = str(s.media['reddit_video']['fallback_url'])
            audio = vid.replace(f'_{vid_h}.', '_audio.')
            v_name = vid.split('/')[3]
            urllib.request.urlretrieve(vid, filename=v_name+'_src.mp4')
            urllib.request.urlretrieve(audio, filename=v_name+'_audio.mp4')
            await hf.convert(ctx, v_name)
            try:
                os.remove(f'{v_name}_src.mp4')
                os.remove(f'{v_name}_audio.mp4')
            except FileNotFoundError:
                pass

            await hf.reply_with_file(ctx, f'{v_name}.mp4')
            
            
        if s.post_hint == 'image':
            f_name=s.url.split('/')[-1]
            urllib.request.urlretrieve(s.url, filename=f_name)
            await ctx.reply(s.url, mention_author=False)
            shutil.move(f'{os.getcwd()}/{f_name}', f'{os.getcwd()}/imgs/{f_name}')
        
        if 'twitter' in s.url:
            pass
            # TODO: add twitter interaction
        
        if 'reddit.com/gallery/' in s.url:
            await ctx.reply(s.url, mention_author=False)


    @commands.command(name='changeprefix', help=f"Change the prefix of the bot (default = {os.getenv('BOT_PREFIX')})")
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
    async def change_prefix(self, ctx, new_prefix):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        old_prefix = prefixes[str(ctx.guild.id)]
        prefixes[str(ctx.guild.id)] = new_prefix

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        
        await ctx.send(f'Changed bot prefix from {old_prefix} to {new_prefix}')


    @commands.command(name='emoteinfo')
    @commands.is_owner()
    async def emote_info(self, ctx, emote):
        print(emote)
        print(int(emote.split(':')[-1][:-1]))
        emoji = self.bot.get_emoji(int(emote.split(':')[-1][:-1]))
        if emoji != None:
            print(type(emoji))
            emoteinfo = {
                'name' : emoji.name,
                'id' : emoji.id,
                'require_colons' : emoji.require_colons,
                'animated' : emoji.animated,
                'managed' : emoji.managed,
                'guild' : emoji.guild,
                'guild_id' : emoji.guild_id,
                'available' : emoji.available,
                'created_at' : emoji.created_at,
                'url' : emoji.url,
                'roles' : emoji.roles,
                'usable' : emoji.is_usable()
            }
            emoji = [f'{key}: {value}' for key,value in emoteinfo.items()]
            await ctx.reply('```'+'\n'.join(emoji)+'```', mention_author=False)
        else:
            await ctx.reply('Not an emote', mention_author=False)


    @commands.command(name='update', hidden=True)
    @commands.is_owner()
    async def update_cogs(self, ctx):
        ext = self.bot.extensions
        for i in ext:
            self.bot.reload_extension(i)
            print(f'Updating {i}')
        # cogs = []


    @commands.command(name='shutdown', help='Shuts the bot down (bot owner only)', hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send('Shutting down')
        await self.bot.close()
        sys.exit(f'Bot shutting down..')


def setup(bot):
    bot.add_cog(ChatUtilities(bot))