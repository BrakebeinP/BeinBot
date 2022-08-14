import discord
import asyncpraw
import os
from discord.ext import commands
from dotenv import load_dotenv
import urllib.request
import subprocess
import shutil
from . import helper_funcs as hf

load_dotenv()

reddit = asyncpraw.Reddit(
    client_id = os.getenv('REDDIT_CLIENT_ID'),
    client_secret = os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='BeinBot v0.0.1 by /u/BrakebeinP'
)



class ChatUtilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            #TODO: add twitter interaction
        
        if 'reddit.com/gallery/' in s.url:
            await ctx.reply(s.url, mention_author=False)



    @commands.command(name='shutdown', help='Shuts the bot down (bot owner only)')
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send('Shutting down')
        await self.bot.close()
        exit()


def setup(bot):
    bot.add_cog(ChatUtilities(bot))