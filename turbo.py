import discord
from discord.ext import commands
import bb_config
import openai, random, json
from collections import defaultdict
from datetime import datetime

openai.api_key = bb_config.openai_key

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
    return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)


class TurboCog(commands.Cog):
    '''
    ChatGPT Support
    Overrides CommandNotFound and sends your message to gpt-3.5-turbo
    '''

    def __init__(self, bot):
        self.bot = bot
        self.name = self.bot.user.name
        self.prompt_lead_in = bb_config.turbo_personality % self.name
        self.chance = bb_config.openai_auto_chance
        self.max_chance = bb_config.openai_auto_chance
        self.max_context = bb_config.openai_max_context
        self.context = defaultdict(list)
        self.chatty = True

    @commands.Cog.listener("on_command_error")
    async def chatgpt_on_command_error(self, ctx, error):
        '''Main function for openai responses'''
        if isinstance(error, commands.CommandNotFound):

            await ctx.typing()
            messages = [{"role": "system", "content": self.prompt_lead_in + " The current time is " + datetime.now().strftime("%c")}]
            for message in self.context[ctx.channel.id]:
                if message[:len(self.name)] == self.name:
                    messages.append({"role": "assistant", "content": message})
                else:
                    messages.append({"role": "user", "content": message})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                frequency_penalty=0.5
            ).choices[0].message.content
            if response[:len(self.name + ": ")] == self.name + ": ":
                tmp = response[len(self.name + ": "):]
            else:
                tmp = response
            await ctx.send(tmp)

    @commands.Cog.listener("on_message")
    async def chatgpt_on_message(self, message):
        '''Function enables there to be a random chance for responses in the General chat'''
        # TODO: Add a heat system for a higher chance of response if theres more talking

        general = self.bot.get_channel(bb_config.general_chat_id)

        if message.content.lower() != self.name.lower() + ", history" and message.content[:3] != "```":
            self.context[message.channel.id].append(message.author.display_name + ": " + message.content)
            if len(self.context[message.channel.id]) > self.max_context:
                self.context[message.channel.id] = self.context[message.channel.id][len(self.context[message.channel.id])-self.max_context:]

        if message.channel == general and message.author != self.bot.user and message.content[:len(self.name)+1].lower() != self.name.lower() + ", " and self.chatty:

            roll = random.SystemRandom().uniform(0, 1)
            
            if self.chance > roll:
                
                await general.typing()
                messages = [{"role": "system", "content": self.prompt_lead_in +
                            " You are in a chat with multiple other users, and each message and response is structured as 'username: message'. Under no circumstances will you try to impersonate anyone else's messages. Do not start your response with '" + self.name + ": '. Act like a human, and contribute to the conversation. The current time is " + datetime.now().strftime("%c")}]

                for message in self.context[message.channel.id]:
                    if message[:len(self.name)] == self.name:
                        messages.append(
                            {"role": "assistant", "content": message})
                    else:
                        messages.append(
                            {"role": "user", "content": message})
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.8,
                    frequency_penalty=0.5
                ).choices[0].message.content
                if response[:len(self.name + ": ")] == self.name + ": ":
                    tmp = response[len(self.name + ": "):]
                else:
                    tmp = response
                await general.send(tmp)
            
            # Chance Recovery 
            if self.chance < self.max_chance:
                self.chance += 0.0025

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def prompt(self, ctx, *, prompt):
        """Construct a direct prompt, without the personality or context."""
        await ctx.typing()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are " + self.name + ", a large language model trained by OpenAI. Answer as concisely as possible. Current Time: " + datetime.now().strftime("%c")},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            frequency_penalty=0
        ).choices[0].message.content
        await ctx.send(response)

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

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def chatty(self, ctx):
        """Toggle Random Chats."""
        if self.chatty:
            self.chatty = False
            await ctx.send("`Disabled Random Chat.`")
        else:
            self.chatty = True
            await ctx.send("`Enabled Random Chat.`")


async def setup(bot):
    await bot.add_cog(TurboCog(bot))
