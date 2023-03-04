import discord
from discord.ext import commands

class ErrorCog(commands.Cog):
    '''This command is just going to fucking error'''

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def trip(self, ctx):
        '''Cause a fucking error I guess'''
        someshit = 1 + "2"
        await ctx.send("Does it please you to hurt me dad")

async def setup(bot):
    await bot.add_cog(ErrorCog(bot))