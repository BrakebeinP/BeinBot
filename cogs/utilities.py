import discord
import asyncpraw
import os
from discord.ext import commands
from dotenv import load_dotenv
import urllib.request
import subprocess

load_dotenv()

reddit = asyncpraw.Reddit(
    client_id = os.getenv('REDDIT_CLIENT_ID'),
    client_secret = os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='BeinBot v0.0.1 by /u/BrakebeinP'
)

def get_boost_lvl(ctx):
    boost_lvl_steps = [0,2,7,14]
    for i, cnt in enumerate(boost_lvl_steps):
            if ctx.guild.premium_subscription_count >= cnt:
                boost_lvl = i
    return boost_lvl

def file_size(file):
    return os.stat(file).st_size/(1024*1024)

async def convert(v_name):
    subprocess.call(
        ['ffmpeg', 
        '-i', f'{v_name}_src.mp4', 
        '-i', f'{v_name}_audio.mp4', 
        '-map', '0:v', '-map', '1:a', 
        '-c:v', 'copy', f'{v_name}.mp4']
        )

class ChatUtilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reddit', help='Reddit vid/img downloader')
    async def reddit_media(self, ctx, cmd_url: str):
        boost_lvl = get_boost_lvl(ctx)
        # print(boost_lvl)
        submission = await reddit.submission(url=cmd_url)
        if submission.is_video:
            # await ctx.edit(embed=None)
            vid_h = submission.media['reddit_video']['height']
            vid = str(submission.media['reddit_video']['fallback_url'])
            audio = vid.replace(f'_{vid_h}.', '_audio.')
            v_name = vid.split('/')[3]
            urllib.request.urlretrieve(vid, filename=v_name+'_src.mp4')
            urllib.request.urlretrieve(audio, filename=v_name+'_audio.mp4')
            await convert(v_name)
            try:
                os.remove(f'{v_name}_src.mp4')
                os.remove(f'{v_name}_audio.mp4')
            except FileNotFoundError:
                pass

            if file_size(f'{v_name}.mp4') > 8 and boost_lvl < 2:
                await ctx.reply(f'Filesize too large, contact {self.bot.owner_id}', mention_author=False)
            # if boost_lvl >= 2:
            # await ctx.reply(file=f'{v_name}.mp4', mention_author=False)
            # else:
            #     pass

    @commands.command(name='shutdown', help='Shuts the bot down (bot owner only)')
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send('Shutting down')
        await self.bot.close()
        exit()


def setup(bot):
    bot.add_cog(ChatUtilities(bot))