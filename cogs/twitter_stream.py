from discord.ext import commands

from tweepy import asynchronous
import tweepy

import json
import os
from dotenv import load_dotenv
import logging


t_logger = logging.getLogger('tweepy')
t_logger.setLevel(logging.DEBUG)
t_handler = logging.FileHandler(filename="logs/tweepy.log", encoding='utf-8', mode='w')
t_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
t_logger.addHandler(t_handler)

load_dotenv()

class TwitterStream(commands.Cog, asynchronous.AsyncStreamingClient):

# **************************************************************
#                         ---meta---
# **************************************************************

    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.tweet_data_channel = self.bot.get_channel(int(os.getenv('BOT_TWEET_DATA_CHANNEL')))
        asynchronous.AsyncStreamingClient.__init__(self, bearer_token=os.getenv('TWITTER_BEARER_TOKEN'), return_type=tweepy.Response, wait_on_rate_limit=False, **kwargs)
        


    async def cog_load(self):
        await self._start()


    def cog_unload(self):
        self.disconnect()

# **************************************************************
#                  ---tweepy client events---
# **************************************************************

    async def on_connect(self):
        await self.bot._log_channel('Connected to twitter')
        t_logger.info("Stream connected")

    async def on_data(self, raw_data):
        await self.bot._log_channel('New tweet')
        tweet_data = json.loads(raw_data)

        with open('json/twitter.json', 'r') as f:
            discord_rules = json.load(f)

        author_id = tweet_data['data']['author_id']
        tweet_id = tweet_data['data']['id']
        # display_name = None
        # avatar_url = None
        user_name = None

        for user in tweet_data['includes']['users']:
            if user['id'] == author_id:
                # display_name = user['name']
                # avatar_url = user['profile_image_url']
                user_name = user['username']

        matching_rules = [rule['tag'] for rule in tweet_data['matching_rules']]
        print(matching_rules)

        # tweet_embed = discord.Embed(title='Original tweet',
        #                     url=f'https://twitter.com/{user_name}/status/{tweet_id}',
        #                     color=0xAFA690,
        #                     description=data['text']) 

        for tag in matching_rules:
            for ch in discord_rules[tag]:
                channel = self.bot.get_channel(int(ch))
                await channel.send(f'https://twitter.com/{user_name}/status/{tweet_id}')
                # webhook = await channel.create_webhook(name=display_name)
                # await webhook.send(embed=tweet_embed, username=display_name, avatar_url=avatar_url)
                # webhooks = channel.webhooks()
                # for hook in webhooks:
                #     await hook.delete()


# **************************************************************
#                 ---stream control commands---
# **************************************************************

    @commands.group(name='twitter', help='Twitter stuffs. For subcommands, try !help twitter', aliases=['tw', 't'])
    @commands.is_owner()
    async def twitter_utils(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Not a valid subcommand (yet... maybe)')



    @twitter_utils.group(name='stream', aliases=['str', 's'])
    @commands.is_owner()
    async def stream_manager(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Not a valid subcommand (yet... maybe)')



    @stream_manager.command(name='start', aliases=['s'])
    async def start_twitter_stream(self, ctx):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        msg = await ctx.reply('Starting strim...')
        await self._start(msg)
        

    @stream_manager.command(name='reset', aliases=['re'])
    async def reset_twitter_rules(self, ctx):
        msg = await ctx.reply('Reseting rules...')

        await self._update_discord_rules(msg=msg)


    @stream_manager.command(name='rules', aliases=['ru'])
    async def twitter_stream_rules(self, ctx):
        rules = await self.get_rules()
        
        if rules.data is not None:
            tw_rules = '\n'.join([rule.tag for rule in rules.data])
            await self.bot._log_channel('```' + tw_rules + '```')
        else:
            await ctx.reply('No rules found.')


    @stream_manager.command(name='update', aliases=['u'])
    async def update_stream_rules(self, ctx):
        await self._update_discord_rules(await ctx.reply('Updating...'))


    @stream_manager.command(name='info', aliases=['i'])
    async def twitter_stream_info(self, ctx):
        info = '\n'.join([self.session, self.task, self.user_agent])
        await self.bot._log_channel(f'```{info}```')

    
    @stream_manager.command(name='clear', aliases=['c', 'cl', 'clr'])
    async def twitter_stream_clear(self, ctx):
        await self._clear_rules(ctx.message)


# **************************************************************
#                ---stream handling methods---
# **************************************************************

    async def _update_discord_rules(self):
        start = 'Updating rules...'
        finish = 'Updated rules'

        self.bot._log_channel(start)

        rules = await self.get_rules()

        if rules.data is not None:
            await self._clear_rules()
        await self._add_rules()

        self.bot._log_channel(finish)

    
    async def _clear_rules(self):
        start = 'Removing old rules...'
        finish = 'Cleaned up old rules'

        await self.bot._log_channel(start)
        
        rules = await self.get_rules()

        if rules.data is not None:
            r = '\n'.join([rule.tag for rule in rules.data])
            await self.bot._log_channel('```' + r + '```')
            for rule in rules.data:
                d = await self.bot._log_channel(f'Deleting rule `{rule.value}`')
                await self.delete_rules(rule.id)
                await d.edit(content=d.content.replace("Deleting", "Deleted"))

        else:
            await self.bot._log_channel('No rules to clear, continuing...')
                
        await self.bot._log_channel(finish)
         
        
    async def _add_rules(self):
        start = 'Adding rules...'
        finish = 'Rules added'

        await self.bot._log_channel(start)

        with open('json/twitter.json', 'r') as f:
            rules = json.load(f)
        
        if len(rules) > 0:
            for rule in rules.keys():
                new_rule = tweepy.StreamRule(value=rule, tag=rule)
                d = await self.bot._log_channel(f"Adding rule: `{new_rule.value}`")
                await self.add_rules(new_rule)
                await d.edit(content=d.content.replace('Adding', 'Added'))
        
        await self.bot._log_channel(finish)

    
    async def _filter(self):
        start = 'Filtering...'
        finish = 'Filtered'

        u_fields = ['name', 'username', 'profile_image_url']
        t_fields = ['entities', 'possibly_sensitive', 'attachments', 'created_at']
        m_fields = ['url', 'variants']
        # exp = ['author_id', 'attachment.media_keys']

        await self.bot._log_channel(start)

        self.filter(expansions='author_id',user_fields=u_fields, tweet_fields=t_fields, media_fields=m_fields)

        await self.bot._log_channel(finish)


    async def _start(self, msg=None):
        await self._clear_rules()

        await self._add_rules()
        
        await self._filter()

        if msg is not None:
            await msg.edit(content=f'{msg.content}\n\nStream started')
    

    async def _add_rule(self, rule):
        new_rule = tweepy.StreamRule(value=rule, tag=rule)
        d = await self.bot._log_channel(f"Adding rule: `{new_rule.value}`")
        await self.add_rules(new_rule)
        await d.edit(content=d.content.replace('Adding', 'Added'))

    
    async def _del_rule(self, rule):
        tw_rules = await self.get_rules()
        if tw_rules.data is not None:
            for r in tw_rules.data:
                if r.value == rule:
                    d = await self.bot._log_channel(f'Deleting rule `{rule}`')
                    await self.delete_rules(r.id)
                    await d.edit(content=d.content.replace("Deleting", "Deleted"))



async def setup(bot):
    await bot.add_cog(TwitterStream(bot))


