import discord, bb_config
from discord.ext import tasks, commands
import vt, aiohttp
from hashlib import sha256

# Async method to load the bytes of a file and return bytes
async def downloadBytes(session: aiohttp.ClientSession, url: str):
	async with session.get(url) as response:
		assert response.status == 200
		return await response.read()

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

class VirusCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.vt_client = vt.Client(bb_config.vt_api_key)
        self.vt_emoji = str(bot.get_emoji(1060966357115605033))
        
    @commands.command()
    async def check_file(self, ctx):
        """Check a file against VirusTotal's Database"""
        await ctx.typing()
        url = ctx.message.attachments[0].url
        session = aiohttp.ClientSession()
        item = await downloadBytes(session, url)
        await session.close()
        vtresponse = await self.vt_client.get_object("/files/%s" % sha256(item).hexdigest())
        good_rep = vtresponse.last_analysis_stats["undetected"]
        ok_rep = vtresponse.last_analysis_stats["harmless"]
        sus_rep = vtresponse.last_analysis_stats["suspicious"]
        bad_rep = vtresponse.last_analysis_stats["malicious"]
        total_rep = good_rep + ok_rep + sus_rep + bad_rep
        if good_rep >= ok_rep and good_rep >= sus_rep and good_rep >= bad_rep:
            verdict = "Clean :white_check_mark:"
        elif ok_rep >= good_rep and ok_rep >= sus_rep and ok_rep >= bad_rep:
            verdict = "Harmless :white_check_mark:"
        elif sus_rep >= good_rep and sus_rep >= bad_rep and sus_rep >= ok_rep:
            verdict = "Suspicious :caution:"
        elif bad_rep >= good_rep and bad_rep >= sus_rep and bad_rep >= ok_rep:
            verdict = "Malicious :no_entry:"
        else: verdict = "Unknown"
        temp = "Name: `%s`\n" % ctx.message.attachments[0].filename
        temp += "Also Known As: `%s`\n" % vtresponse.meaningful_name
        temp += "Negative Reports: %s / %s\n" % (bad_rep + sus_rep, total_rep)
        temp += "Verdict: %s\n" % verdict
        temp += "Results from %s" % self.vt_emoji
        await ctx.send(temp, suppress_embeds=True)

    @commands.command()
    async def check_url(self, ctx, *, url: str):
        """Check a Website URL against VirusTotal's Database"""
        await ctx.typing()
        url_id = vt.url_id(url)
        vtresponse = await self.vt_client.get_object("/urls/{}", url_id)
        good_rep = vtresponse.last_analysis_stats["undetected"]
        ok_rep = vtresponse.last_analysis_stats["harmless"]
        sus_rep = vtresponse.last_analysis_stats["suspicious"]
        bad_rep = vtresponse.last_analysis_stats["malicious"]
        total_rep = good_rep + ok_rep + sus_rep + bad_rep
        if good_rep >= ok_rep and good_rep >= sus_rep and good_rep >= bad_rep:
            verdict = "Clean :white_check_mark:"
        elif ok_rep >= good_rep and ok_rep >= sus_rep and ok_rep >= bad_rep:
            verdict = "Harmless :white_check_mark:"
        elif sus_rep >= good_rep and sus_rep >= bad_rep and sus_rep >= ok_rep:
            verdict = "Suspicious :caution:"
        elif bad_rep >= good_rep and bad_rep >= sus_rep and bad_rep >= ok_rep:
            verdict = "Malicious :no_entry:"
        else: verdict = "Unknown"
        temp = "URL: `%s`\n" % vtresponse.url
        temp += "Actual Destination: `%s`\n" % vtresponse.last_final_url
        temp += "Negative Reports: %s / %s\n" % (bad_rep + sus_rep, total_rep)
        temp += "Verdict: %s\n" % verdict
        temp += "Results from %s" % self.vt_emoji
        await ctx.send(temp, suppress_embeds=True)

async def setup(bot):
    await bot.add_cog(VirusCog(bot))