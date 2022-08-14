import subprocess
import os
import shutil

def get_boost_lvl(ctx):
    boost_lvl_steps = [0,2,7,14]
    for i, cnt in enumerate(boost_lvl_steps):
            if ctx.guild.premium_subscription_count >= cnt:
                boost_lvl = i
    return boost_lvl

def file_size(file):
    return os.stat(file).st_size/(1024*1024)

async def convert(ctx, v_name):
    try:
        subprocess.call(
            ['ffmpeg', 
            '-i', f'{v_name}_src.mp4', 
            '-i', f'{v_name}_audio.mp4', 
            '-map', '0:v', '-map', '1:a', 
            '-c:v', 'copy', f'{v_name}.mp4']
            )
    except:
        ctx.send('ffmpeg not installed', mention_author=False)

async def reply_with_file(ctx, filename):
    vids = ('.mp4', '.avi', '.mkv')
    imgs = ('.jpg', '.png', '.jpeg', '.gif', '.bmp', '.tif', '.tiff')
    if filename.endswith(vids):
        try:
            await ctx.reply(file=filename, mention_author=False)
        except:
            await ctx.reply(f'Filesize too large, contact bot owner', mention_author=False)

        shutil.move(f'{os.getcwd()}/{filename}', f'{os.getcwd()}/vids/{filename}')

    elif filename.endswith(imgs):
        print('test')
        await ctx.reply(file=filename, mention_author=False)
        shutil.move(f'{os.getcwd()}/{filename}', f'{os.getcwd()}/imgs/{filename}')