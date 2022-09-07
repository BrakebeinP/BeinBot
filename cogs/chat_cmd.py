from discord.ext import commands
import json


class ChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='derp', help='derp')
    async def derp(self, ctx):
        await ctx.reply('Derp.', mention_author=False)


    @commands.command(name='addcommand', help='Adds a custom command to the server:\nsyntax= {prefix}addcommand {new command name} {bot response}')
    async def add_command(self, ctx, new_cmd, *, cmd_resp):
        with open('json/cmd.json', 'r') as f:
            cmds = json.load(f)

        if new_cmd in self.bot.commands:
            ctx.reply("Command is a standard bot command, couldn't add.")

        else:
            if str(new_cmd) not in cmds[str(ctx.guild.id)].keys():
                guild_cmds = cmds[str(ctx.guild.id)]
                created_at = ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                cmd = {
                    'response' : str(cmd_resp),
                    'created_by' : str(ctx.author.id),
                    'created_at' : created_at
                }
                guild_cmds[str(new_cmd)] = cmd
                cmds[str(ctx.guild.id)][str(new_cmd)] = cmd
                with open('json/cmd.json', 'w') as f:
                    json.dump(cmds, f, indent=4)
                await ctx.reply(f'Added command "{new_cmd}": {cmd_resp}', mention_author=False)

            elif str(new_cmd) in cmds[str(ctx.guild.id)].keys():
                await ctx.reply('Command already exits:\n' +
                    f'```Created by: {await self.bot.fetch_user(int(cmds[str(ctx.guild.id)][str(new_cmd)]["created_by"]))}\n' +
                    f"Created at: {cmds[str(ctx.guild.id)][str(new_cmd)]['created_at']}```")

            else:
                await ctx.reply('Unable to add command :PepeS:')
    
    @commands.command(name='delcommand', help='Deletes the custom command')
    async def delete_command(self, ctx, cmd_name):
        with open('json/cmd.json', 'r') as f:
            cmds = json.load(f)

        if str(ctx.author.id) == cmds[str(ctx.guild.id)][str(cmd_name)]['created_by']:
            try:
                del(cmds[str(ctx.guild.id)][cmd_name])
                await ctx.reply(f'Deleted command {cmd_name}')

            except:
                await ctx.reply("Command doesn't exist.")

            with open('json/cmd.json', 'w') as f:
                json.dump(cmds, f, indent=4)
        else:
            ctx.reply(f'Unable to delete command "{cmd_name}".\n'+
            'Reason: You did not make this command.')

    @commands.command(name='commandinfo', help='Gives information about the command (if it exists)')
    async def command_info(self, ctx, cmd_name):
        if str(cmd_name) in self.bot.commands:
            cmd = self.bot.get_command(cmd_name)
            await ctx.reply(f'Standard bot command:\n{cmd.help}')
        else:
            with open('json/cmd.json', 'r') as f:
                cmds = json.load(f)
            if str(cmd_name) in cmds[str(ctx.guild.id)].keys():
                cmd_info = cmds[str(ctx.guild.id)][str(cmd_name)]
                cmd_info['created_by'] = await self.bot.fetch_user(int(cmd_info['created_by']))
                info_response = '\n'.join([f'{key}: {value}' for key, value in cmd_info.items()])
                await ctx.reply(f"""{cmd_name}:```{info_response}```""")
            else:
                await ctx.reply('Not a command: ' + str(cmd_name))

       

async def setup(bot):
    await bot.add_cog(ChatCommands(bot))