import discord
from discord.ext import commands
import random

class SimpleCog(commands.Cog):
    '''The base stuff'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['hi', 'howdy', 'hello'])
    async def hello(self, ctx):
        """Greet the bot."""
        await ctx.send('Hello.')

    @commands.command()
    async def choose(self, ctx, *choices : str):
        """Chooses between multiple choices."""
        random.seed()
        if (len(choices) < 2):
            await ctx.send("?")
        else: await ctx.send(random.choice(choices))

async def setup(bot):
    await bot.add_cog(SimpleCog(bot))
