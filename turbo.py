import discord
from discord.ext import commands
import bb_config
import openai, random, json
from collections import defaultdict

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
        self.chance = bb_config.openai_auto_chance
        self.context = defaultdict(list)
        self.max_context = bb_config.openai_max_context
        self.prompt_lead_in = bb_config.turbo_personality
        self.last_response = ""

    @commands.Cog.listener("on_command_error")
    async def chatgpt_on_command_error(self, ctx, error):
        '''Main function for openai responses'''
        if isinstance(error, commands.CommandNotFound):
            await ctx.typing()
            self.context[ctx.message.author.name].append(ctx.message.author.display_name + ": " + ctx.message.content)
            messages = [{"role": "system", "content": self.prompt_lead_in}]
            for item in self.context[ctx.message.author.name]:
                if item[:len(bb_config.openai_name + ": ")] == bb_config.openai_name + ": ":
                    messages.append({"role": "assistant", "content": item})
                else: messages.append({"role": "user", "content": item})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            if response.choices[0].message.content[:len(bb_config.openai_name + ": ")] == bb_config.openai_name + ": ": 
                tmp = response.choices[0].message.content[len(bb_config.openai_name + ": "):] 
            else : tmp = response.choices[0].message.content 
            await ctx.send(tmp)
            self.context[ctx.message.author.name].append(bb_config.openai_name + ": " + tmp)

    @commands.Cog.listener("on_message")
    async def chatgpt_on_message(self, message):
        '''Function enables there to be a random chance for responses in the General chat'''
        # TODO: Add a heat system for a higher chance of response if theres more talking
        # Recover chance if told to chill
        if self.chance < bb_config.openai_auto_chance:
            self.chance += 0.01
        # Roll for chance
        roll = random.SystemRandom().uniform(0,1)
        # Get General Chat
        general = self.bot.get_channel(bb_config.general_chat_id)
        # Check for General Chat, That the message wasnt sent by BB,
        # that the message wasnt already directed towards BB, and that we pass the roll
        if message.channel == general and message.author != self.bot.user and message.content[:2] != "BB" and self.chance > roll:
            await general.typing()
            # Using chat for context was gettin weird, so I'm appending the prompt lead in to try to keep her focused.
            messages = [{"role": "system", "content": self.prompt_lead_in + " You are in a chat with multiple users, each message structured as 'username: message'. Contribute to the conversation naturally."}]
            chat = [message async for message in general.history(limit=self.max_context)]
            for message in chat[::-1]:
                if message.author.display_name == bb_config.openai_name:
                    messages.append({"role": "assistant", "content": message.author.display_name + ": " + message.content})
                else: messages.append({"role": "user", "content": message.author.display_name + ": " + message.content})
            #messages.append({"role": "assistant", "content": self.last_response})
            #messages.append({"role": "user", "content": message.author.display_name + ": " + message.content})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            if response.choices[0].message.content[:4] == "BB: ": 
                tmp = response.choices[0].message.content[4:] 
            else : tmp = response.choices[0].message.content 
            self.last_response = tmp
            await general.send(tmp)

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def prompt(self, ctx, *, prompt):
        await ctx.typing()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are BB, a large language model trained by OpenAI. Answer as concisely as possible."},
                    {"role": "user", "content": prompt}
                ]
        ).choices[0].message.content
        await ctx.send(response)

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def mindwipe(self, ctx):
        self.context = defaultdict(list)
        self.last_response = ""
        await ctx.send("What were we talking about?")

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def history(self, ctx, *, name = None):
        if name == None:
            name = ctx.message.author.name
        if self.context[name]:
            tmp = "```\n"
            for item in self.context[name]:
                tmp += item + "\n"
            tmp += "```"
            await ctx.send(tmp)
        else:
            await ctx.send("`No history for that user.`")

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def chill(self, ctx):
        self.chance = 0
        await ctx.send("Fine, jeez.")
        
async def setup(bot):
    await bot.add_cog(TurboCog(bot))