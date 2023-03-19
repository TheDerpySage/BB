import discord
from discord.ext import commands
import bb_config
import openai

openai.api_key = bb_config.openai_key

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

class DavinciCog(commands.Cog):
    '''Davinci Text Completion Support'''

    def __init__(self, bot):
        self.bot = bot
        self.max_context = 10
        self.note = ""
        self.context = []

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def prompt(self, ctx, *, prompt):
        self.context.append(prompt + "\n")
        if len(self.context) > self.max_context:
            self.context = self.context[len(self.context)-self.max_context:]
        await ctx.typing()
        text = self.note
        for item in self.context:
            text += item
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.9,
            max_tokens=2049,
            frequency_penalty=0.5,
            presence_penalty=0.0
        ).choices[0].text
        await ctx.send(response)
        self.context.append(response)
        if len(self.context) > self.max_context:
            self.context = self.context[len(self.context)-self.max_context:]

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def note(self, ctx, *, prompt):
        await ctx.typing()
        note = prompt + "\n\n"
        await ctx.send("Note set.")

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def history(self, ctx):
        await ctx.typing()
        if self.context:
            temp = "```\n" + self.note
            for item in self.context:
                temp += item
            temp +="```"
        else: temp = "No history."
        await ctx.send(temp)

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def wipe(self, ctx):
        await ctx.typing()
        self.context = []
        await ctx.send("Memory wiped.")
        
async def setup(bot):
    await bot.add_cog(DavinciCog(bot))