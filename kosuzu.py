import discord
from discord.ext import commands
import bb_config
import requests, random, json
from collections import defaultdict
from datetime import datetime

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
    return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

class KosuzuCog(commands.Cog):
    '''
    Pygmalion being hosted on KoboldAI Support
    Overrides CommandNotFound and sends your message to Kosuzu
    '''

    def __init__(self, bot):
        self.bot = bot
        self.name = self.bot.user.name
        self.prompt = bb_config.kosuzu_personality % self.name
        self.chance = bb_config.openai_auto_chance
        self.max_context = bb_config.openai_max_context
        self.context = defaultdict(list)

    @commands.Cog.listener("on_command_error")
    async def chatgpt_on_command_error(self, ctx, error):
        '''Main function for openai responses'''
        if isinstance(error, commands.CommandNotFound):

            await ctx.typing()
            messages = self.prompt
            for message in self.context[ctx.channel.id]:
                messages += message + '\n'
            messages += "%s:" % self.name
            
            parameters = {
                "prompt": messages,
                "temperature": 0.8,
                "top_p": 0.9,
                "singleline": "True"
            }

            response = requests.post("http://kosuzu.thederpysage.com:5000/api/v1/generate", json=parameters)

            if response.status_code == 200:
                await ctx.send(json.loads(response.text)['results'][0]['text'].strip())
            elif response.status_code == 503:
                await ctx.send("`Server is busy; please try again later...`")
            elif response.status_code == 507:
                await ctx.send("`Server ran out of memory, yell at Majora about this...`")
            else: 
                await ctx.send("`" f"Status Code: {response.status_code}, Response: {response.text}" "`")

    @commands.Cog.listener("on_message")
    async def chatgpt_on_message(self, message):
        '''Function enables there to be a random chance for responses in the General chat'''
        # TODO: Add a heat system for a higher chance of response if theres more talking

        general = self.bot.get_channel(bb_config.general_chat_id)

        if message.content.lower() != self.name.lower() + ", history" and message.content[:3] != "```":
            self.context[message.channel.id].append(message.author.display_name + ": " + message.content)
            if len(self.context[message.channel.id]) > self.max_context:
                self.context[message.channel.id] = self.context[message.channel.id][len(self.context[message.channel.id])-self.max_context:]

        if message.channel == general and message.author != self.bot.user and message.content[:len(self.name)+1].lower() != self.name.lower() + ", ":

            roll = random.SystemRandom().uniform(0, 1)
            
            if self.chance > roll:
                
                await general.typing()
                messages = self.prompt
                for message in self.context[message.channel.id]:
                    messages += message + '\n'
                messages += "%s:" % self.name
                
                parameters = {
                    "prompt": messages,
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "singleline": "True"
                }

                response = requests.post("http://kosuzu.thederpysage.com:5000/api/v1/generate", json=parameters)

                if response.status_code == 200:
                    await ctx.send(json.loads(response.text)['results'][0]['text'].strip())
                elif response.status_code == 503:
                    await ctx.send("`Server is busy; please try again later...`")
                elif response.status_code == 507:
                    await ctx.send("`Server ran out of memory, yell at Majora about this...`")
                else: 
                    await ctx.send("`" f"Status Code: {response.status_code}, Response: {response.text}" "`")
            else:
                pass

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def mindwipe(self, ctx, mod = ""):
        """Clears the bots memory from this channel, or add all to clear all."""
        if mod.lower() == "all":
            self.context = defaultdict(list)
            await ctx.send("Brain hurty...")
        else:
            self.context[ctx.channel.id] = []
            await ctx.send("What were we talking about?")
        

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def history(self, ctx, *, name=None):
        """See bots memory for the current channel."""
        if self.context[ctx.channel.id]:
            tmp = "```\n"
            for item in self.context[ctx.channel.id]:
                tmp += item + "\n"
            tmp += "```"
            await ctx.send(tmp)
        else:
            await ctx.send("`No history in this channel.`")

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def chill(self, ctx):
        """Temporarily Zero out bots random chance to respond."""
        self.chance = 0
        await ctx.send("Fine, jeez.")


async def setup(bot):
    await bot.add_cog(KosuzuCog(bot))
