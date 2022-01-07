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
        await ctx.trigger_typing()
        #Check Nginx
        result = socket_test('192.168.1.6',80)
        if result == 0:
            toadHealth = ":white_check_mark:"
            public = True
        else:
            toadHealth = ":no_entry:(%s)" % result
            public = False
        #Check Web .com
        result = socket_test('192.168.1.7',80)
        if result == 0:
            webHealth = ":white_check_mark:"
            if public == False:
                webHealth = ":warning: NO PUBLIC ACCESS"
        else: webHealth = ":no_entry:(%s)" % result
        #Check NAS
        result = socket_test('192.168.1.4',445)
        if result == 0:
            nasHealth = ":white_check_mark:"
            files = True
        else: 
            nasHealth = ":no_entry:(%s)" % result
            files = False
        #Check Web .moe
        result = socket_test('192.168.1.9',80)
        if result == 0:
            moeHealth = ":white_check_mark:"
            if public == False:
                moeHealth = ":warning: NO PUBLIC ACCESS"
        else: moeHealth = ":no_entry:(%s)" % result
        #Check Plex
        result = socket_test('192.168.1.2',32400)
        if result == 0:
            plexHealth = ":white_check_mark:"
            if files == False:
                plexHealth = ":warning: NO FILES"
            elif public == False: 
                plexHealth = ":warning: NO PUBLIC ACCESS; Use https://app.plex.tv/"
        else: plexHealth = ":no_entry:(%s)" % result
        #webmail
        result = socket_test('192.168.1.12',443)
        if result == 0:
            roundHealth = ":white_check_mark:"
        else: roundHealth = ":no_entry:(%s)" % result
        #Postfix
        result = socket_test('192.168.1.12',587)
        if result == 0:
            postHealth = ":white_check_mark:"
        else: postHealth = ":no_entry:(%s)" % result
        #Output
        temp = ("**SERVICES**" +
        "\n\n~Nginx~" + "\nStatus:\t" + toadHealth + "\n*Reverse Proxy*" +
        "\n\n~com Website~ " + "\nStatus:\t" + webHealth + "\nhttp://www.thederpysage.com/" +
        "\n\n~NAS~ " + "\nStatus:\t" + nasHealth + "\n*File Server*" +
        "\n\n~moe Website~ " + "\nStatus:\t" + moeHealth + "\nhttp://www.thederpysage.moe/" +
        "\n\n~Plex~" + "\nStatus:\t" + plexHealth + "\nhttp://plex.thederpysage.moe/" + 
        "\n\n~E-MAIL~" + "\nPostfix:\t" + postHealth + "\nWebmail:\t" + roundHealth + "\nhttps://portland.thederpysage.com")
        await ctx.send(temp)

    @commands.command()
    async def servers(self, ctx):
        """Server Status"""
        await ctx.trigger_typing()
        if bool_ping("192.168.1.2"):
            nagato = ":white_check_mark:"
        else : nagato = ":no_entry:"
        if bool_ping("192.168.1.3"):
            akagi = ":white_check_mark:"
        else : akagi = ":no_entry:"
        if bool_ping("192.168.1.6"):
            laffey = ":white_check_mark:"
        else : laffey = ":no_entry:"
        if bool_ping("192.168.1.7"):
            mutsu = ":white_check_mark:"
        else : mutsu = ":no_entry:"
        if bool_ping("192.168.1.4"):
            kaga = ":white_check_mark:"
        else : kaga = ":no_entry:"
        if bool_ping("192.168.1.13"):
            uni = ":white_check_mark:"
        else : uni = ":no_entry:"
        if bool_ping("192.168.1.15"):
            yama = ":white_check_mark:"
        else : yama = ":no_entry:"
        if bool_ping("192.168.1.12"):
            port = ":white_check_mark:"
        else : port = ":no_entry:"
        temp = ("**SERVERS**" +
        "\nAkagi:\t" + akagi +
        "\nKaga:\t" + kaga +
        "\nLaffey:\t" + laffey +
        "\nNagato:\t" + nagato +
        "\nMutsu:\t" + mutsu +
        "\nUnicorn:\t" + uni + 
        "\nYamashiro:\t" + yama +
        "\nPortland:\t" + port)
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

    @tasks.loop(seconds=120.0)
    async def monitor(self):
        '''Reporting for downtime for mission critical servers.'''
        await self.bot.wait_until_ready()
        await self.reporting.process()

    @commands.command(name="process")
    @commands.check(is_super)
    async def force_process(self, ctx):
        """Force an update"""
        await ctx.send("OK.")
        await self.reporting.process()

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


def setup(bot):
    bot.add_cog(ServerCog(bot))