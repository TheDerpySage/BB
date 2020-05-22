import discord
from discord.ext import commands

class RolesCog(commands.Cog):
    '''Simple Opt In/Out Role Delegation'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def watch(self, ctx):
        """Ready up."""
        optin_role= "Watcher"
        role = discord.utils.get(ctx.message.author.guild.roles, name=optin_role)
        if (discord.utils.get(ctx.message.author.roles, name=optin_role) == None):
            try:
                await ctx.message.author.add_roles(role)
                await ctx.send("Watcher given to " + ctx.message.author.name + ".")
            except discord.Forbidden:
                await ctx.send("I don't have permission to mess with roles!")
        else: 
            try:
                await ctx.message.author.remove_roles(role)
                await ctx.send("Watcher removed from " + ctx.message.author.name + ".")
            except discord.Forbidden:
                await ctx.send("I don't have permission to mess with roles!")

    @commands.command(pass_context=True)
    async def bother(self, ctx):
        bother_role = "But Nobody Bother Buko"
        role = discord.utils.get(ctx.message.author.guild.roles, name=bother_role)
        if (discord.utils.get(ctx.message.author.roles, name=bother_role) == None):
            try:
                await ctx.message.author.add_roles(role)
                await ctx.send("Don't bother " + ctx.message.author.name + ".")
            except discord.Forbidden:
                await ctx.send("I don't have permission to mess with roles!")
        else:
            try:
                await ctx.message.author.remove_roles(role)
                await ctx.send("Everyone bother " + ctx.message.author.name + ".")
            except discord.Forbidden:
                await ctx.send("I don't have permission to mess with roles!")

    

def setup(bot):
    bot.add_cog(RolesCog(bot))