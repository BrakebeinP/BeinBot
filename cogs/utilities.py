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
from main import COGS


load_dotenv()

reddit = asyncpraw.Reddit(
    client_id = os.getenv('REDDIT_CLIENT_ID'),
    client_secret = os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='BeinBot v0.0.2 by /u/BrakebeinP'
)



class ChatUtilities(commands.Cog, name='Utilities'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='createchannel', hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def create_channel(self, ctx, channel_name='kek'):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating new channel: {channel_name} in {guild.name}')
            await guild.create_text_channel(channel_name)


    @commands.command(name='reddit', help='Reddit vid/img downloader')
    async def reddit_media(self, ctx, cmd_url: str):
        
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
        with open('json/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        old_prefix = prefixes[str(ctx.guild.id)]
        prefixes[str(ctx.guild.id)] = new_prefix

        with open('json/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        
        await ctx.send(f'Changed bot prefix from {old_prefix} to {new_prefix}')


    @commands.command(name='emoteinfo', help='Posts info about an emote', hidden=True) # TODO: remove hidden once this works for all emotes
    @commands.is_owner()
    async def emote_info(self, ctx, emote, /):
        emote_id = int(emote.split(':')[-1][:-1])
        print(emote)
        print(emote_id)
        try:
            emoji = self.bot.get_emoji(emote_id)
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
        except:
            try:
                emoji = discord.PartialEmoji.from_str(emote)
                await emoji.save()
            except:
                print('NOPE')
                await ctx.reply('Not an emote', mention_author=False)
        else:
            await ctx.reply('Not an emote', mention_author=False)


    @commands.command(name='owner', help='Tells you who the bot owner is')
    async def get_owner(self, ctx):
        owner = await self.bot.fetch_user(int(self.bot.owner_id))
        await ctx.reply(f'Bot owner: {owner}', mention_author=False)


    @commands.command(name='update', hidden=True)
    @commands.is_owner()
    async def update_cogs(self, ctx):
        await self.bot.log_channel.send('Reloading:\n```- ' + '\n- '.join(COGS) + '```', mention_author=False)

        for i in COGS:
            if i != __name__:
                self.bot.reload_extension(i)
                await self.bot.log_channel.send(f'Reloaded {i}')

        await self.bot.log_channel.send(f'Reloaded {__name__}')
        await self.bot.log_channel.send('Reloaded:\n```' + '\n- '.join(COGS) + '```', mention_author=False)

        await self.bot.reload_extension(__name__)
        


    @commands.command(name='botinfo', hidden=True)
    @commands.is_owner()
    async def get_bot_info(self, ctx):
        print(self.bot.user.id)
        bot_info = {
            'id': self.bot.user.id,
            'avatar': self.bot.user.avatar,
            'created_at': self.bot.user.created_at,
            'default_avatar': self.bot.user.default_avatar,
            'display_name': self.bot.user.display_name,
            'discriminator': self.bot.user.discriminator,
            'display_avatar': self.bot.user.display_avatar,
            'name': self.bot.user.name}
        print('getto')
        info = [key+': '+value for key,value in bot_info.items()]
        await ctx.reply('```' + '\n'.join(info)+'```', mention_author=False)

    @commands.command(name='cogs', hidden=True)
    @commands.is_owner()
    async def self_cogs(self, ctx):
        cogs = '\n'.join([cog for cog in self.bot.extensions])
        await self.bot.log_channel.send(cogs)


    @commands.command(name='shutdown', hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        with open('last_ctx.txt', 'w') as f:
            f.write(str(ctx.channel.id))
        await self.bot.log_channel.send('Shutting down')
        await self.bot.close()
        sys.exit(f'Bot shutting down..')


async def setup(bot):
    await bot.add_cog(ChatUtilities(bot))