import discord
from discord.ext import commands
import bot_config

def is_super(ctx):
	return (ctx.message.author.id == bot_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bot_config.super_role) != None)

class UsersCog(commands.Cog):
    '''User Management'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        general_channel = self.bot.get_channel(bot_config.general_chat_id)
        log_channel = self.bot.get_channel(bot_config.log_chat_id)
        await log_channel.send(member.name + " left")
        await general_channel.send("Seeya, " + member.mention + "!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        general_channel = self.bot.get_channel(bot_config.general_chat_id)
        log_channel = self.bot.get_channel(bot_config.log_chat_id)
        await log_channel.send(member.name + " joined")
        #await member.add_roles(discord.utils.get(member.guild.roles, name="The Boys"))
        await general_channel.send("Welcome " + member.mention + "!")

    # Example Role Toggle Command
    # @commands.command(pass_context=True)
    # async def ror2(self, ctx):
    #     """Grant yourself the Risky Rainy"""
    #     optin_role= "Risky Rainy"
    #     role = discord.utils.get(ctx.message.author.guild.roles, name=optin_role)
    #     if (discord.utils.get(ctx.message.author.roles, name=optin_role) == None):
    #         try:
    #             await ctx.message.author.add_roles(role)
    #             await ctx.send("%s given to %s." % (ctx.message.author.name, optin_role))
    #         except discord.Forbidden:
    #             await ctx.send("I don't have permission to mess with roles!")
    #     else: 
    #         try:
    #             await ctx.message.author.remove_roles(role)
    #             await ctx.send("%s removed from %s" % (ctx.message.author.name, optin_role))
    #         except discord.Forbidden:
    #             await ctx.send("I don't have permission to mess with roles!")

async def setup(bot):
    await bot.add_cog(UsersCog(bot))
