from discord.ext import commands
import json


class ChatCommands(commands.Cog, name='Regular commands'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='derp', help='derp')
    async def derp(self, ctx):
        await ctx.reply('Derp.', mention_author=False)


    @commands.command(name='addcommand', help='Adds a custom command to the server:\nsyntax= {prefix} {new command name} {bot response}')
    async def add_command(self, ctx, new_cmd, *, cmd_resp):
        with open('commands.json', 'r') as f:
            cmds = json.load(f)
        if str(new_cmd) not in cmds.keys():
            cmds[str(ctx.guild.id)][str(new_cmd)] = str(cmd_resp)
            with open('commands.json', 'w') as f:
                json.dump(cmds, f, indent=4)
            await ctx.reply(f'Added command "{new_cmd}": {cmd_resp}')
        else:
            await ctx.reply('Unable to add command :PepeS:')
            json.dump(cmds, indent=4)

        await ctx.send(f'command {new_cmd}, {cmd_resp}')


    @commands.command(name='owner', help='Gets the user ID of the bot owner')
    async def get_owner(self, ctx):
        await ctx.reply(f'Owner: {self.bot.owner_id}', mention_author=False)
       

def setup(bot):
    bot.add_cog(ChatCommands(bot))