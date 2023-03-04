import discord
from discord.ext import commands
import random

class SimpleCog(commands.Cog):
    '''The base stuff'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['hi', 'howdy'])
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

    # @commands.command(aliases=['is', 'are', 'am', 'does', 'will', 'can', 'do', 'could', 'did', 'should', 'would', 'was'])
    # async def ask(self, ctx, *, message: str = None ):
    #     """Ask a Yes or No Question."""
    #     if message != None:
    #         random.seed()
    #         intensity = random.randint(1,20)
    #         if intensity == 1:
    #             await ctx.send("Absolutely not.")
    #         elif intensity < 10:
    #             await ctx.send("No.")
    #         elif intensity == 10:
    #             await ctx.send("Maybe.")
    #         elif intensity < 20:
    #             await ctx.send("Yes.")
    #         elif intensity == 20:
    #             await ctx.send("Definitely.")
    #         else: await ctx.send("Go fuck yourself.")
    #     else: await ctx.send("?")

    @commands.command()
    async def roll(self, ctx, *, message: str = None):
        """Shoot dice. Acceptable format is NdX. Where N is number of dice and X is how many sides."""
        if message != None:
            if message.index('d') >= 0:
                nums = message.split('d')
                try:
                    dice = int(nums[0])
                    sides = int(nums[1])
                except:
                    await ctx.send("?")
                else: 
                    if dice and sides > 0:
                        response = ""
                        for x in range(dice):
                            random.seed()
                            response += "%s, " % random.randint(1, sides)
                        await ctx.send(response[:-2])
        else: await ctx.send("?")

    @commands.command(aliases=["diss", "disrespect"])
    async def trash_talk(self, ctx, *, message: str = None ):
        await ctx.send("The test results came back from the hospital.\nYou are a stage five dumbass.")

async def setup(bot):
    await bot.add_cog(SimpleCog(bot))
