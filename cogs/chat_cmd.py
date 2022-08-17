import discord
from discord.ext import commands


class ChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='derp', help='derp')
    async def derp(self, ctx):
        await ctx.reply('Derp.', mention_author=False)


    @commands.command(name='owner')
    async def get_owner(self, ctx):
        await ctx.reply(f'Owner: {self.bot.get_user(self.bot.owner_id)}')
       

def setup(bot):
    bot.add_cog(ChatCommands(bot))