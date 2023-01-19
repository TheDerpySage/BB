import discord
from discord.ext import tasks, commands
import bb_config

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

class TrackCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.member = 0
        self.present = False
        self.tracking = False
        
    def cog_unload(self):
        self.monitor.cancel()

    @commands.command(hidden=True)
    @commands.check(is_super)
    async def track(self, ctx, *, who : int):
        """Start Track User"""
        self.member = self.bot.get_guild(bb_config.server_id).get_member(who)
        if self.member.raw_status == "offline":
            self.present = False
        else:
            self.present = True
        self.monitor.start()
        await self.bot.get_channel(bb_config.log_chat_id).send("Tracking...")

    @commands.command(hidden=True)
    @commands.check(is_super)
    async def who(self, ctx):
        """Whom are you tracking"""
        if self.member != 0:
            await ctx.send(self.member.display_name)
        else : await ctx.send("Nobody... yet...")

    @commands.command(hidden=True)
    @commands.check(is_super)
    async def untrack(self, ctx):
        """Stop Tracking User"""
        self.member = 0
        self.present = False
        self.tracking = False
        self.monitor.cancel()
        await self.bot.get_channel(bb_config.log_chat_id).send("OK")

    @tasks.loop(seconds=300)
    async def monitor(self):
        '''Watch for user to be online'''
        await self.bot.wait_until_ready()
        if not self.present:
            if self.member.raw_status != "offline":
                await self.bot.get_channel(bb_config.log_chat_id).send("%s Alert" % self.member.display_name)
                self.present = True
        else:
            if self.member.raw_status == "offline":
                self.present = False

async def setup(bot):
    await bot.add_cog(TrackCog(bot))