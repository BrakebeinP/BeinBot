import discord
from discord.ext import commands

async def is_brakebein(ctx):
    return ctx.author.id == 107454639254798336

class ChatCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='derp', help='derp')
    async def derp(self, ctx):
        await ctx.reply('Derp.', mention_author=False)

    @commands.command(name='createchannel')
    @commands.has_role('admin')
    async def create_channel(self, ctx, channel_name='kek'):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating new channel: {channel_name} in {guild.name}')
            await guild.create_text_channel(channel_name)
    
    @commands.command(name='owner')
    async def get_owner(self, ctx):
        await ctx.reply(f'Owner ID: {self.bot.owner_id}')
    

def setup(bot):
    bot.add_cog(ChatCommands(bot))