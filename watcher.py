import discord
from discord.ext import commands
import random

class WatcherCog(commands.Cog):
    '''Simple Opt In/Out Role Delegation'''

    def __init__(self, bot):
        self.bot = bot
        self.optin_role= "Watcher"

    @commands.command(pass_context=True)
    async def opt_in(self, ctx):
        """Ready up."""
        try:
            role = discord.utils.get(ctx.message.author.guild.roles, name=self.optin_role)
            if (discord.utils.get(ctx.message.author.roles, name=self.optin_role) == None):
                try:
                    await ctx.message.author.add_roles(role)
                    await ctx.send(self.optin_role + " given to " + ctx.message.author.name + ".")
                except discord.Forbidden:
                    await ctx.send("I don't have permission to mess with roles!")
            else: await ctx.send("You already have " + optin_role + ".")
        except:
            await ctx.send("No such role. Maybe you forgot to edit the file?")

    @commands.command(pass_context=True)
    async def opt_out(self, ctx):
        """Unready."""
        try:
            role = discord.utils.get(ctx.message.author.guild.roles, name=self.optin_role)
            if (discord.utils.get(ctx.message.author.roles, name=self.optin_role) != None):
                try:
                    await ctx.message.author.remove_roles(role)
                    await ctx.send(self.optin_role + " removed from " + ctx.message.author.name + ".")
                except discord.Forbidden:
                    await ctx.send("I don't have permission to mess with roles!")
            else: await ctx.send("You don't have " + optin_role + ".")
        except:
            await ctx.sends("No such role. Maybe you forgot to edit the file?")
    

def setup(bot):
    bot.add_cog(WatcherCog(bot))