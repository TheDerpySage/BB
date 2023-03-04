import discord
from discord.ext import commands
import bb_config
import openai, random, json

openai.api_key = bb_config.openai_key

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

class DavinciCog(commands.Cog):
    '''Davinci Support'''

    def __init__(self, bot):
        self.bot = bot
        self.chance = bb_config.openai_auto_chance
        self.num_context = 10
        self.prompt_lead_in = bb_config.davinci_personality
        self.last_response = "Hello."

    @commands.Cog.listener("on_message")
    async def openai_on_message(self, message):
        roll = random.SystemRandom().uniform(0,1)
        general = self.bot.get_channel(bb_config.general_chat_id)
        if message.channel == general and message.author != self.bot.user and message.content[:2] != "BB":
            if self.chance >= roll:
                await general.typing()
                prompt = self.prompt_lead_in
                messages = [message async for message in general.history(limit=self.num_context)]
                for message in messages:
                    prompt += message.author.display_name + ": " + message.content + "\n"
                prompt += bb_config.openai_name  + ": "
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    temperature=0.5,
                    max_tokens=100,
                    top_p=0.3,
                    frequency_penalty=0.5,
                    presence_penalty=0.0
                )
                await general.send(response.choices[0].text)

    @commands.Cog.listener("on_command_error")
    async def openai_on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.typing()
            prompt = self.prompt_lead_in
            prompt += bb_config.openai_name + ": " + self.last_response + "\n" 
            prompt += ctx.message.author.display_name + ": " + ctx.message.content + "\n"
            prompt += bb_config.openai_name  + ": "
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.5,
                max_tokens=100,
                top_p=0.3,
                frequency_penalty=0.5,
                presence_penalty=0.0
            )
            self.last_response = response.choices[0].text
            await ctx.send(response.choices[0].text)

    @commands.command(pass_context=True, aliases=['is', 'are', 'am', 'does', 'will', 'can', 'do', 'could', 'did', 'should', 'would', 'was', 'who', 'what', 'where', 'when', 'why', 'how', 'pick'])
    async def question(self, ctx):
        await ctx.typing()
        prompt = self.prompt_lead_in
        prompt += bb_config.openai_name + ": " + self.last_response + "\n" 
        prompt += ctx.message.author.display_name + ": " + ctx.message.content + "\n"
        prompt += bb_config.openai_name  + ": "
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=100,
            top_p=0.3,
            frequency_penalty=0.5,
            presence_penalty=0.0
        )
        self.last_response = response.choices[0].text
        await ctx.send(response.choices[0].text)

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def prompt(self, ctx, *, prompt):
        await ctx.typing()
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.9,
            max_tokens=2049,
            frequency_penalty=0.5,
            presence_penalty=0.0
        )
        await ctx.send(response.choices[0].text)
        
async def setup(bot):
    await bot.add_cog(DavinciCog(bot))