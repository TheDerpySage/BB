import discord
from discord.ext import commands
import bb_config
import aiohttp

# Self made check since is_owner() doesnt appear to be working and includes server owner
# For Myself and the Server Owner


def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

# Async method to load the bytes of a file and return bytes


async def downloadBytes(session: aiohttp.ClientSession, url: str):
	async with session.get(url) as response:
		assert response.status == 200
		return await response.read()


class AdminCog(commands.Cog):
	'''Majora/Server Owner Only stuff'''

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="say", aliases=['echo'], hidden=True)
	@commands.check(is_super)
	async def echo(self, ctx, *, message: str):
		await ctx.send(message)
		print(message)

	@commands.command(name="exit", hidden=True)
	@commands.check(is_super)
	async def exit_bot(self, ctx):
		await ctx.send("Shutting down...")
		exit()

	# Cog Management
	@commands.command(name='load', hidden=True)
	@commands.check(is_super)
	async def extension_load(self, ctx, *, cog: str):
		"""Command which Loads a Module. Remember to use dot path. e.g: cogs.owner"""
		try:
			self.bot.load_extension(cog)
		except Exception as e:
			await ctx.send('**`ERROR: %s`**' % e)
		else:
			await ctx.send('**`SUCCESS`**')

	@commands.command(name='unload', hidden=True)
	@commands.check(is_super)
	async def extension_unload(self, ctx, *, cog: str):
		"""Command which Unloads a Module. Remember to use dot path. e.g: cogs.owner"""
		try:
			self.bot.unload_extension(cog)
		except Exception as e:
			await ctx.send('**`ERROR: %s`**' % e)
		else:
			await ctx.send('**`SUCCESS`**')

	@commands.command(name='reload', hidden=True)
	@commands.check(is_super)
	async def extension_reload(self, ctx, *, cog: str):
		"""Command which Reloads a Module. Remember to use dot path. e.g: cogs.owner"""
		try:
			self.bot.unload_extension(cog)
			self.bot.load_extension(cog)
		except Exception as e:
			await ctx.send('**`ERROR: %s`**' % e)
		else:
			await ctx.send('**`SUCCESS`**')

	# Server Channel Specific
	@commands.command(name='yell', hidden=True)
	@commands.check(is_super)
	async def yell(self, ctx, channel_id, *, message: str):
		channel = self.bot.get_channel(int(channel_id))
		await channel.send(message)

	# User Specific
	@commands.command(name='tell', hidden=True)
	@commands.check(is_super)
	async def tell(self, ctx, target, *, message: str):
		if (target[:1] == "<"):
            # If an @ Mention is passed
			user = discord.utils.get(
			    ctx.message.author.guild.members, id=int(target[3:len(target)-1]))
		else:
            # If just a name is passed
			user = discord.utils.get(ctx.message.author.guild.members, name=target)
			if(not isinstance(user, discord.abc.User)):
                # If The name that was passed is the guild-side nickname
				user = discord.utils.get(ctx.message.author.guild.members, nick=target)
		if (isinstance(user, discord.abc.User)):
			if user.dm_channel == None:
				await user.create_dm()
			await user.dm_channel.send(message)
		else : await ctx.send("No such user.")

	@commands.command(name='pfp', hidden=True)
	@commands.check(is_super)
	async def update_profile_picture(self, ctx):
		try:
			url = ctx.message.attachments[0].url
			session = aiohttp.ClientSession()
			item = await downloadBytes(session, url)
			await session.close()
			await self.bot.user.edit(password=None, avatar=item)
		except Exception as e:
			await ctx.send('**`ERROR: %s`**' % e)
		else:
			await ctx.send('**`SUCCESS`**')

	@commands.command(name='name', hidden=True)
	@commands.check(is_super)
	async def update_profile_name(self, ctx, *, newname: str):
		try:
			await self.bot.user.edit(password=None, username=newname)
		except Exception as e:
			await ctx.send('**`ERROR: %s`**' % e)
		else:
			await ctx.send('**`SUCCESS`**')

	@commands.command(aliases=['about'])
	async def credits(self, ctx):
		'''Show credits.'''
		await ctx.send("`BB created by TheDerpySage.\nHosted on vinny.thederpysage.com.\nQuestions/Concerns? Contact via Discord.\n@TheDerpySage#2049`")

def setup(bot):
	bot.add_cog(AdminCog(bot))
