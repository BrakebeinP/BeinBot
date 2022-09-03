from discord.ext import commands
import discord

from tweepy import asynchronous
import tweepy

import asyncio

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

    def __init__(self, bot, **kwargs):
        self.bot = bot
        asynchronous.AsyncStreamingClient.__init__(self, bearer_token=os.getenv('TWITTER_BEARER_TOKEN'), return_type=tweepy.Response, wait_on_rate_limit=False, **kwargs)

    async def cog_load(self):
        await self._start()

# **************************************************************

    async def on_connect(self):
        await self.bot.log_channel.send('Twitter.on_connect: Connected to twitter')
        t_logger.info("Stream connected")

    async def on_data(self, raw_data):
        data = json.loads(raw_data)
        print_data = json.dumps(data, indent=4)
        await self.bot.log_channel.send(f'Twitter.on_data:```json\n{print_data}```')

# **************************************************************

    # def on_data(self, raw_data):
    #     data = json.loads(raw_data)
    #     print(data['entities']['id'])
    #     print(data['entities']['text'])
    #     # print(f'https://twitter.com/twitter/status/{tweet.id}')
    #     rules = await self.get_rules()
    #     rule = data['matching_rules'][0]['tag']
    #     channel = await self.get_channel(int(rules[rule]['channel']))
    #     await channel.send('```json\n' + json.dumps(data) + '```')


    # async def send_tweet(self, ctx, tweet):
    #     fields = ['name', 'username', 'profile_image_url']
    #     tweet_info = self.tw_util.get_tweet(tweet.id, expansions='author_id', user_fields=fields)
    #     tweet_author = tweet_info.includes['users'][0]
    #     webhook = await ctx.create_webhook(name=tweet_author.name)
    #     embed = discord.Embed(
    #         title='Original tweet', 
    #         url=f'https://twitter.com/{tweet_author.username}/status/{tweet.id}',
    #         color=0xAFA690)
    #     await webhook.send(embed, username=tweet_author.name, avatar_url=tweet_author.profile_image_url)

    #     webhooks = ctx.channel.webhooks()
    #     for webhook in webhooks:
    #         await webhook.delete()
    

    @commands.group(name='twitter', help='Twitter stuffs. For subcommands, try !help twitter', aliases=['tw', 't'])
    @commands.is_owner()
    async def twitter_utils(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Not a valid subcommand (yet... maybe)', mention_author=False)



    @twitter_utils.group(name='stream', alias=['str', 's'])
    @commands.is_owner()
    async def stream_manager(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Not a valid subcommand (yet... maybe)', mention_author=False)



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
            await self.bot.log_channel.send('\n'.join([rule for rule in rules.data]))
        else:
            await ctx.reply('No rules found.', mention_author=False)


    @stream_manager.command(name='update', aliases=['u'])
    async def update_stream_rules(self, ctx):
        await self._update_discord_rules(await ctx.reply('Updating...', mention_author=False))


    @stream_manager.command(name='info', aliases=['i'])
    async def twitter_stream_info(self, ctx):
        await self.bot.log_channel.send('```'+'\n'.join([self.session, self.task, self.user_agent])+'```')

    
    @stream_manager.command(name='clear', aliases=['c', 'cl', 'clr'])
    async def twitter_stream_clear(self, ctx):
        await self._clear_rules(ctx.message)


# **************************************************************

    
    async def _update_discord_rules(self, msg=None, /):
        start = 'Updating rules...'
        finish = 'Updated rules'

        rules = await self.get_rules()

        if msg is not None:
            await msg.edit(content=f'{msg.content}\n{start}')
            if rules.data is not None:
                msg = await self._clear_rules(msg)
            msg = await self._add_rules(msg)
        else:
            if rules.data is not None:
                await self._clear_rules()
            await self._add_rules()

        if msg is not None:
            await msg.edit(content=f'{msg.content}\n{finish}')

    
    async def _clear_rules(self):
        start = 'Twitter._clear_rules: Removing old rules...'
        finish = 'Twitter._clear_rules: Cleaned up old rules'

        await self.bot.log_channel.send(start)
        
        rules = await self.get_rules()
        await self.bot.log_channel.send(rules)

        if rules.data is not None:
            for rule in rules.data:
                d = await self.bot.log_channel.send(f'Twitter: Deleting rule `{rule}`')
                await self.delete_rules(rule.id)
                await d.edit(content=f'Twitter: Deleted rule `{rule.value}`')

        else:
            await self.bot.log_channel.send('Twitter: No rules to clear, continuing...')
                
        await self.bot.log_channel.send(finish)
         
        
    async def _add_rules(self):
        start = 'Twitter._add_rules: Adding rules...'
        finish = 'Twitter._add_rules: Rules added'

        await self.bot.log_channel.send(start)

        with open('json/twitter.json', 'r') as f:
            rules = json.load(f)
        
        if len(rules) > 0:
            for rule in rules.keys():
                new_rule = tweepy.StreamRule(value=rule, tag=rule)
                d = await self.bot.log_channel.send(f"Twitter: Adding rule: `{new_rule}`")
                await self.add_rules(new_rule)
                await d.edit(content=f'Twitter: Added rule `{new_rule.value}`')
        
        await self.bot.log_channel.send(finish)

    
    async def _filter(self):
        start = 'Twitter._filter: Filtering...'
        finish = 'Twitter._filter: Filtered'

        u_fields = ['name', 'username', 'profile_image_url']
        t_fields = ['entities', 'possibly_sensitive', 'attachments', 'created_at']
        m_fields = ['url', 'variants']

        await self.bot.log_channel.send(start)

        self.filter(expansions='author_id',user_fields=u_fields, tweet_fields=t_fields, media_fields=m_fields)

        await self.bot.log_channel.send(finish)


    async def _start(self, msg=None):
        await self._clear_rules()

        await self._add_rules()
        
        await self._filter()

        if msg is not None:
            await msg.edit(content=f'{msg.content}\n\nStream started')


# **************************************************************

    
    def cog_unload(self):
        super(asynchronous.AsyncStreamingClient, self).disconnect()


async def setup(bot):
    await bot.add_cog(TwitterStream(bot))


