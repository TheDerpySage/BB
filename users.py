import discord
from discord.ext import commands
import bb_config

def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

# Helper Method to search for a user
def search_user(bot, who):
    try:
        # If Mention or ID is passed (approach the substring from the right, since it can include @! or just @ seemingly at random)
        if (who[:1] == "<"):
            x = bot.get_user(int(who[-19:-1]))
            return x
        else :
            x = bot.get_user(int(who))
            return x
    except:
        # If Name or Nick is passed
        for x in bot.get_all_members():
            if (x.name == who) or (x.nick == who):
                return x
        return None

class UsersCog(commands.Cog):
    '''User Management'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        general_channel = self.bot.get_channel(bb_config.general_chat_id)
        log_channel = self.bot.get_channel(bb_config.log_chat_id)
        await log_channel.send(member.name + " left")
        await general_channel.send("Seeya, " + member.mention + "!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        general_channel = self.bot.get_channel(bb_config.general_chat_id)
        log_channel = self.bot.get_channel(bb_config.log_chat_id)
        await log_channel.send(member.name + " joined")
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
    async def anime(self, ctx):
        """Grant yourself the Anime Club role"""
        anime_role = "Anime Club"
        role = discord.utils.get(ctx.message.author.guild.roles, name=anime_role)
        if (discord.utils.get(ctx.message.author.roles, name=anime_role) == None):
            try:
                await ctx.message.author.add_roles(role)
                await ctx.send("Welcome to Anime Club, " + ctx.message.author.name + ".")
            except discord.Forbidden:
                await ctx.send("I don't have permission to mess with roles!")
        else:
            try:
                await ctx.message.author.remove_roles(role)
                await ctx.send("No more Anime Club for " + ctx.message.author.name + ".")
            except discord.Forbidden:
                await ctx.send("I don't have permission to mess with roles!")

    @commands.command(pass_context=True)
    @commands.check(is_super)
    async def jail(self, ctx, *, target = None):
        """Grant other people the GBJ Role"""
        jail_role = "Gay Baby Jail"
        role = discord.utils.get(ctx.message.guild.roles, name=jail_role)
        if target != None:
            user = search_user(self.bot, target)
        else: 
            user = ctx.message.author
        if user == None:
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
        if target != None:
            user = search_user(self.bot, target)
        else: 
            user = ctx.message.author
        if user != None:
            await ctx.send(user.avatar_url)
        else : await ctx.send("No such user.")

def setup(bot):
    bot.add_cog(UsersCog(bot))