import discord
from discord.ext import commands
import bb_config

class SniperCog(commands.Cog):
    '''Sniper!!!'''

    def __init__(self, bot):
        self.bot = bot
        self.log = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.log[message.channel] = message.author.name + ": " + message.content
    
    @commands.command(pass_context=True)
    async def snipe(self, ctx):
        if(ctx.channel in self.log):
            await ctx.send(self.log[ctx.channel])
        else : await ctx.send("Nothing to snipe...")

def setup(bot):
    bot.add_cog(SniperCog(bot))