import discord
from discord.ext import commands
import discord.abc
import sys
import traceback
from datetime import datetime
import bot_config


def get_prefix(bot, msg):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = [bot.user.name[0:1].lower()+'$', bot.user.name+', ',
                bot.user.name.lower()+', ']
    # Check to see if we are outside of a guild. e.g DM's etc.
    if msg.channel is None:
        return ''
    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, msg)


desc = '''Written and Developed by TheDerpySage'''

startup_extensions = bot_config.default_extensions
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix,
                   description=desc, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Game(name='Use '+bot.user.name[0:1].lower()+'$help'))
    if __name__ == '__main__':
        for extension in startup_extensions:
            try:
                await bot.load_extension(extension)
            except:
                print('Failed to load extension ' + extension, file=sys.stderr)
                traceback.print_exc()
    print('Successfully logged in and booted...!')
    # Log Channel for her DMs
    log_channel = bot.get_channel(bot_config.log_chat_id)
    if not bot_config.CONNECTED:
        await log_channel.send("Connected.")
        bot_config.CONNECTED = True
    else:
        await log_channel.send("Connection was dropped, reconnected now.")


@bot.event
async def on_message(message):
    log_channel = bot.get_channel(bot_config.log_chat_id)
    # Checks if its a DM
    if isinstance(message.channel, discord.abc.PrivateChannel):
        # Makes sure it's not her talking, may be a good idea to delete just to make sure DMs are actually sending...
        if message.author.id != bot_config.client_id:
            # Name, ID, and message from the DM
            temp = message.author.name + " : " + message.content
            # Post any attachments too
            for item in message.attachments:
                temp += '\n' + item.url
            # Sends it all to the Log Channel
            await log_channel.send(temp)
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You have no power here.")
    else:
        await ctx.send("`" + str(error) + "`")

bot.run(bot_config.token, reconnect=True)
