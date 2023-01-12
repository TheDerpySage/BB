import discord
from discord.ext import tasks, commands
import bb_config
import socket
from urllib.request import urlopen
import os
import subprocess
from datetime import timedelta
import asyncio
from emailer import Emailer

# For Myself, Server Owner, and a pre-designated Super Role
def is_super(ctx):
	return (ctx.message.author.id == bb_config.owner_id) or (ctx.message.author == ctx.message.guild.owner) or (discord.utils.get(ctx.message.author.roles, name=bb_config.super_role) != None)

# Some Neccessary Functions 
def ping(host):
    #OS Neutral Ping
    assert (os.name == 'posix' or os.name == 'nt'), "Unrecognized os.name"
    if os.name == 'posix':
        result = subprocess.run(['ping', '-c', '1', '-W', '2', host], stdout=subprocess.DEVNULL)
        return result.returncode
    elif os.name == 'nt':
        result = subprocess.run(['ping', '/r', '1', '/w', '2', host], stdout=subprocess.DEVNULL)
        return result.returncode

def string_ping(host):
    response = ping(host)
    if response == 0:
        return (host + " is reachable.")
    else:
        return (host + " is unreachable.")

def bool_ping(host):
    response = ping(host)
    if response == 0:
        return True
    else:
        return False

def socket_test(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    temp = sock.connect_ex((host, port))
    if temp == 0: sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    return temp

def bool_socket(host, port):
    response = socket_test(host, port)
    if response == 0:
        return True
    else:
        return False

# Reporting Object 
class Reporting(object):
    def __init__(self, bot, channel_id, givenServers, givenServices):
        self.servers = givenServers
        self.services = givenServices
        #the report list keeps track of down servers already reported so we dont repeat notifications
        self.report = []
        #the channel we send notifications to
        self.channel = bot.get_channel(channel_id)
        self.emailer = Emailer(bb_config.host, bb_config.username, bb_config.password)

    async def process(self):
        temp = self.report.copy()
        for x in self.servers: 
            # x[name, ip]
            if bool_ping(x[1]):
                if x[0] in self.report:
                    temp.remove(x[0])
                    await self.channel.send(":white_check_mark: " + x[0] + " is back up.")
                #else still up so no need to repeat
            else : 
                if x[0] not in self.report:
                    temp.append(x[0])
                    await self.channel.send(":no_entry: " + x[0] + " is unresponsive.")
                #else still unresponsive so no need to repeat
        for x in self.services:
            # x[name, ip, port]
            if bool_socket(x[1], x[2]):
                if x[0] in self.report:
                    temp.remove(x[0])
                    await self.channel.send(":white_check_mark: " + x[0] + " is back up.")
            else : 
                if x[0] not in self.report:
                    temp.append(x[0])
                    await self.channel.send(":no_entry: " + x[0] + " is down.")
        # Get our differences based on our two reports
        recovered = set(self.report) - set(temp)
        died = set(temp) - set(self.report)
        # Overwrite the report
        self.report = temp
        # Notify if there's something worth reporting
        if bb_config.send_alerts_to != '':
            if recovered or died:
                body = ""
                if died:
                    body += "The following have stopped responding\n"
                    for x in died:
                        body += x.split('.')[0] + "\n"
                    body += "\n"
                if recovered:
                    body += "The following have recovered\n"
                    for x in recovered:
                        body += x.split('.')[0] + "\n"
                    body += "\n"
                body += "Please login and check running services."
                self.emailer.send_email(bb_config.send_alerts_to, 'Alert!', body)


# Cog Proper
class ServerCog(commands.Cog):
    '''Server functions'''

    def __init__(self, bot):
        self.bot = bot
        if bb_config.reporting:
            self.reporting = Reporting(self.bot, bb_config.reporting_chat_id, bb_config.serverList, bb_config.serviceList)
            print('Starting Monitoring Task...')
            self.monitor.start()

    def cog_unload(self):
        self.monitor.cancel()

    @commands.command(aliases=['ip'])
    async def current_ip(self, ctx):
        """Returns Current Public IP"""
        curIP = urlopen('http://ip.42.pl/raw').read().decode('utf-8')
        await ctx.send(curIP)

    @commands.command(aliases=['system', 'server', 'health'])
    async def system_info(self, ctx):
        """Returns information about her Server"""
        host = socket.getfqdn()
        # This annoys linters because it is not OS Neutral. It's ok since she lives on a Linux host.
        ldavg_tup = os.getloadavg()
        ldavg_string = ""
        for num in ldavg_tup:
            ldavg_string += "%s " % round(num, 2)
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(timedelta(seconds = uptime_seconds))
        await ctx.send("**System Info**\nHost: " + host + "\nLoad: " + ldavg_string + "\nUptime: " + uptime_string)

    @commands.command()
    async def services(self, ctx):
        """Service Status"""
        await ctx.typing()
        temp = "--**SERVICES**--\n"
        for x in bb_config.serviceList:
            if bool_socket(x[1], x[2]):
                temp += x[0] + ": :white_check_mark:\n"
            else : temp += x[0] + ": :no_entry:\n"
        await ctx.send(temp)

    @commands.command()
    async def servers(self, ctx):
        """Server Status"""
        await ctx.typing()
        temp = "--**SERVERS**--\n"
        for x in bb_config.serverList:
            if bool_ping(x[1]):
                temp += x[0] + ": :white_check_mark:\n"
            else : temp += x[0] + ": :no_entry:\n"
        await ctx.send(temp)
    
    @commands.command(name="wake", hidden=True)
    @commands.check(is_super)
    async def wol(self, ctx, *, mac):
        subprocess.run(['wakeonlan', mac], stdout=subprocess.DEVNULL)
        await ctx.send("Wake-on-LAN packet sent to " + mac)

    @commands.command(name="slap", hidden=True)
    @commands.check(is_super)
    async def Lily(self, ctx):
        await ctx.send("Letting Lily know she can stop.")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("192.168.1.2", 42069))
        s.send(bytes("EXIT","utf-8"))
        s.close()

    @tasks.loop(seconds=bb_config.checkInterval)
    async def monitor(self):
        '''Reporting for downtime for mission critical servers.'''
        await self.bot.wait_until_ready()
        if bb_config.reporting:
            await self.reporting.process()

    @commands.command(name="process")
    @commands.check(is_super)
    async def force_process(self, ctx):
        """Force an update"""
        if bb_config.reporting:
            await ctx.send("OK, checking...")
            await self.reporting.process()
        else : await ctx.send("Monitoring not enabled.")

    @commands.command(name="broken")
    async def whats_broken(self, ctx):
        """Report whats dead"""
        if self.reporting.report:
            temp = "Here's what's dead...\n```\n"
            for x in self.reporting.report:
                temp += x + "\n"
            temp += "```"
            await ctx.send(temp)
        else: await ctx.send("Report is empty.")


async def setup(bot):
    await bot.add_cog(ServerCog(bot))
