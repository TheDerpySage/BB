import discord
from discord.ext import commands
import bb_config
import openai, random, json

openai.api_key = bb_config.openai_key

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

class ChatGPTCog(commands.Cog):
    '''
    ChatGPT Support
    Overrides CommandNotFound and sends your message to gpt-3.5-turbo
    '''

    def __init__(self, bot):
        self.bot = bot
        self.chance = bb_config.openai_auto_chance
        self.context = {} # {user.display_name : messages[]}
        self.prompt_lead_in = bb_config.turbo_personality
        self.last_response = ""

    @commands.Cog.listener("on_command_error")
    async def chatgpt_on_command_error(self, ctx, error):
        '''Main function for openai responses'''
        if isinstance(error, commands.CommandNotFound):
            await ctx.typing()
            messages = [{"role": "system", "content": self.prompt_lead_in}]
            messages.append({"role": "assistant", "content": self.last_response})
            messages.append({"role": "user", "content": ctx.message.author.display_name + ": " + ctx.message.content})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            if response.choices[0].message.content[:3] == "BB:": 
                tmp = response.choices[0].message.content[3:] 
            else : tmp = response.choices[0].message.content 
            self.last_response = tmp
            await ctx.send(tmp)

    @commands.Cog.listener("on_message")
    async def chatgpt_on_message(self, message):
        '''Function enables there to be a random chance for responses in the General chat'''
        # TODO: Add a heat system for a higher chance of response if theres more talking
        roll = random.SystemRandom().uniform(0,1)
        general = self.bot.get_channel(bb_config.general_chat_id)
        if message.channel == general and message.author != self.bot.user and message.content[:2] != "BB":
            if self.chance >= roll:
                await general.typing()
                messages = [{"role": "system", "content": self.prompt_lead_in}]
                messages.append({"role": "assistant", "content": self.last_response})
                messages.append({"role": "user", "content": message.author.display_name + ": " + message.content})
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
    async def mindwipe(self, ctx):
        self.context = {}
        self.last_response = ""
        await ctx.send("What were we talking about?")

async def setup(bot):
    await bot.add_cog(ChatGPTCog(bot))