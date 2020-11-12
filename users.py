import discord
from discord.ext import commands
import bb_config

def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

class UsersCog(commands.Cog):
    '''User Management'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        general_channel = self.bot.get_channel(bb_config.general_chat_id)
        await general_channel.send("Seeya, " + member.mention + "!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        general_channel = self.bot.get_channel(bb_config.general_chat_id)
        await member.add_roles(discord.utils.get(member.guild.roles, name="The Boys"))
        await general_channel.send("Welcome " + member.mention + "!")

    @commands.command(pass_context=True)
    async def watch(self, ctx):
        """Grant yourself the Watcher Role"""
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
        """Grant yourself the But Nobody Bother Buko Role"""
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

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def jail(self, ctx, *, target = None):
        """Grant other people the GBJ Role"""
        jail_role = "Gay Baby Jail"
        role = discord.utils.get(ctx.message.guild.roles, name=jail_role)
        if (target == None):
            # If nothings passed
            user = ctx.message.author
        elif (target[:1] == "<"):
            # If an @ Mention is passed
            user = discord.utils.get(ctx.message.author.guild.members, id=int(target[3:len(target)-1]))
        else : 
            # If just a name is passed
            user = discord.utils.get(ctx.message.author.guild.members, name=target)
            if(not isinstance(user, discord.abc.User)):
                # If The name that was passed is the guild-side nickname
                user = discord.utils.get(ctx.message.author.guild.members, nick=target)
        if (isinstance(user, discord.abc.User)):
            if (discord.utils.get(user.roles, name=jail_role) == None):
                try:
                    await user.add_roles(role)
                    await ctx.send("Welcome to GBJ,  " + user.name + ".")
                except discord.Forbidden:
                    await ctx.send("I don't have permission to mess with roles!")
            else:
                try:
                    await user.remove_roles(role)
                    await ctx.send("Freed " + user.name + ".")
                except discord.Forbidden:
                    await ctx.send("I don't have permission to mess with roles!")
        else : await ctx.send("No such user.")

    @commands.command(name="avatar", pass_context=True)
    async def get_pfp(self, ctx, *, target = None):
        if (target == None):
            # If nothings passed
            user = ctx.message.author
        elif (target[:1] == "<"):
            # If an @ Mention is passed
            user = discord.utils.get(ctx.message.author.guild.members, id=int(target[3:len(target)-1]))
        else : 
            # If just a name is passed
            user = discord.utils.get(ctx.message.author.guild.members, name=target)
            if(not isinstance(user, discord.abc.User)):
                # If The name that was passed is the guild-side nickname
                user = discord.utils.get(ctx.message.author.guild.members, nick=target)
        if (isinstance(user, discord.abc.User)): 
            await ctx.send(user.avatar_url)
        else : await ctx.send("No such user.")

def setup(bot):
    bot.add_cog(UsersCog(bot))