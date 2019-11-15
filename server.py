import discord
from discord.ext import commands
import socket
from urllib.request import urlopen
import os
from datetime import timedelta
import asyncio

class ServerCog(commands.Cog):
    '''Server functions'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ip'])
    async def current_ip(self, ctx):
        """Returns Current Public IP"""
        curIP = urlopen('http://ip.42.pl/raw').read().decode('utf-8')
        await ctx.send(curIP)

    @commands.command(aliases=['system', 'server', 'health'])
    async def system_info(self, ctx):
        """Returns information about her Server"""
        host = socket.getfqdn()
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
        result = socket_test('laffey.thederpysage.com',80)
        if result == 0:
            toadHealth = ":white_check_mark:"
            public = True
        else:
            toadHealth = ":no_entry:(%s)" % result
            public = False
        #Check Web .com
        result = socket_test('mutsu.thederpysage.com',80)
        if result == 0:
            webHealth = ":white_check_mark:"
            if public == False:
                webHealth = ":warning: NO PUBLIC ACCESS"
        else: webHealth = ":no_entry:(%s)" % result
        #Check NAS
        result = socket_test('kaga.thederpysage.com',445)
        if result == 0:
            nasHealth = ":white_check_mark:"
            files = True
        else: 
            nasHealth = ":no_entry:(%s)" % result
            files = False
        #Check Web .moe
        result = socket_test('fubuki.thederpysage.com',80)
        if result == 0:
            moeHealth = ":white_check_mark:"
            if public == False:
                moeHealth = ":warning: NO PUBLIC ACCESS"
        else: moeHealth = ":no_entry:(%s)" % result
        #Check Minecraft
        result = socket_test('fubuki.thederpysage.com',25565)
        if result == 0:
            mineHealth = ":white_check_mark:"
        else: mineHealth = ":no_entry:(%s)" % result
        #Check Plex
        result = socket_test('nagato.thederpysage.com',32400)
        if result == 0:
            plexHealth = ":white_check_mark:"
            if files == False:
                plexHealth = ":warning: NO FILES"
            elif public == False: 
                plexHealth = ":warning: NO PUBLIC ACCESS; Use https://app.plex.tv/"
        else: plexHealth = ":no_entry:(%s)" % result
        #Output
        temp = ("**SERVICES**" +
        "\n\n~Nginx~" + "\nStatus:\t" + toadHealth + "\n*Reverse Proxy*" +
        "\n\n~com Website~ " + "\nStatus:\t" + webHealth + "\nhttp://www.thederpysage.com/" +
        "\n\n~NAS~ " + "\nStatus:\t" + nasHealth + "\n*File Server*" +
        "\n\n~moe Website~ " + "\nStatus:\t" + moeHealth + "\nhttp://www.thederpysage.moe/" +
        "\n\n~Minecraft~ " + "\nStatus:\t" + mineHealth + "\nminecraft.thederpysage.moe" +
        "\n\n~Plex~" + "\nStatus:\t" + plexHealth + "\nhttp://plex.thederpysage.moe/")
        await ctx.send(temp)

    @commands.command()
    async def servers(self, ctx):
        """Server Status"""
        await ctx.trigger_typing()
        if bool_ping("nagato.thederpysage.com"):
            nagato = ":white_check_mark:"
        else : nagato = ":no_entry:"
        if bool_ping("akagi.thederpysage.com"):
            akagi = ":white_check_mark:"
        else : akagi = ":no_entry:"
        if bool_ping("laffey.thederpysage.com"):
            laffey = ":white_check_mark:"
        else : laffey = ":no_entry:"
        if bool_ping("mutsu.thederpysage.com"):
            mutsu = ":white_check_mark:"
        else : mutsu = ":no_entry:"
        if bool_ping("fubuki.thederpysage.com"):
            fubuki = ":white_check_mark:"
        else : fubuki = ":no_entry:"
        if bool_ping("kaga.thederpysage.com"):
            kaga = ":white_check_mark:"
        else : kaga = ":no_entry:"
        temp = ("**SERVERS**" +
        "\nAkagi:\t" + akagi +
        "\nKaga:\t" + kaga +
        "\nLaffey:\t" + laffey +
        "\nNagato:\t" + nagato +
        "\nMutsu:\t" + mutsu +
        "\nFubuki:\t" + fubuki)
        await ctx.send(temp)

    @commands.command(aliases=['ping'])
    async def output_ping(self, ctx, hostname):
        """Pings a given host to check if it's reachable"""
        await ctx.trigger_typing()
        await ctx.send(string_ping(hostname))

class Reporting(object):
    def __init__(self, bot, channel_id):
        #the report list keeps track of down servers already reported so we dont repeat notifications
        self.report = []
        #the channel we send notifications to
        self.channel = bot.get_channel(channel_id)
    async def process_server(self, hostname):
        if bool_ping(hostname):
            if hostname in self.report:
                self.report.remove(hostname)
                await self.channel.send(":white_check_mark: " + hostname.split('.')[0] + " is back up.")
            #else still up so no need to repeat
        else : 
            if hostname not in self.report:
                self.report.append(hostname)
                await self.channel.send(":no_entry: " + hostname.split('.')[0] + " is unresponsive.")
            #else still unresponsive so no need to repeat

async def monitor(bot):
    '''Reporting for downtime for mission critical servers.'''
    await bot.wait_until_ready()
    reporting = Reporting(bot, 585841199156559892)
    serverList = ["akagi.thederpysage.com", "kaga.thederpysage.com", "laffey.thederpysage.com", "nagato.thederpysage.com", "mutsu.thederpysage.com"]
    print('Starting Monitoring Task...')
    while True:
        for x in serverList: 
            await reporting.process_server(x)
        await asyncio.sleep(120)

def ping(host):
    #This is a Linux Ping, edit for Windows
    response = os.system("ping -c 1 -W 2 " + host)
    return response

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

def setup(bot):
    bot.loop.create_task(monitor(bot))
    bot.add_cog(ServerCog(bot))