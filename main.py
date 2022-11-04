import asyncio
import os
from re import A
import subprocess
import logging as log
from xml.dom import minidom
import DiceBot3
# import discord
# from discord.ext import commands
import disnake
from disnake.ext import commands

#BEGIN Logfile
logFile = 'output.log'
logLevel = log.INFO #Possible values:  INFO,WARNING,ERROR,CRITICAL,DEBUG
log.basicConfig(filename=logFile,level=logLevel)
#END Logfile

log.info("Dice Servitor initializing...")

#BEGIN Config File
configFile = 'config.xml'
#os.chdir('/root/diceServitor')
config = minidom.parse(configFile)
BOT_VERSION = config.getElementsByTagName('botVersion')[0].firstChild.data
DISCORD_TOKEN = config.getElementsByTagName('discordToken')[0].firstChild.data
SYS_PASS = config.getElementsByTagName('adminPassword')[0].firstChild.data
#END Config File

log.info("Dice Servitor initialized.")

# bot = commands.Bot(command_prefix="!")
bot = commands.InteractionBot()
#Ping
# @bot.slash_command(
#     help = "Responds with 'pong'!",
#     brief = "Responds with 'pong'!"
# )
# async def ping(ctx):
#     await ctx.channel.send("pong")

#Slash Command Timer
@bot.slash_command()
async def timer(inter: disnake.ApplicationCommandInteraction, seconds: int):
    await inter.response.send_message(f"Setting a timer for {seconds} seconds.")
    await asyncio.sleep(seconds)
    await inter.followup.send(f"{inter.author.mention}, your timer expired!")

#Slash Command Ping
@bot.slash_command(
    name="sping",
)
async def sping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message("Spong!")

#test input slash command
@bot.slash_command(name="repeat",
description="Repeats what is entered")
async def repeat(inter, input: str):
    await inter.response.send_message(input)

#Roll
@bot.slash_command(
    name="roll",
    description= """Rolls dice. Syntax:  roll 3d10<=5#comment""",
)
async def roll(inter, input: str):
    await inter.response.send_message("Rolling: " + input + '\n' + str(DiceBot3.diceRolling(input)))

# #Rtchargen
@bot.slash_command(
    help = """Does the basic rolls for creating a Rogue Trader character all at once.
              Rolls 9x 2d10+25 for characteristics plus an additional, optional replacment
              Rolls 1d5 for wounds
              Rolls 1d10 for fate""",
    brief = "Rolls dice for Rogue Trader chargen"
)
async def rtchargen(ctx, *args):
    async with ctx.typing():
        log.info("Character generation command invoked, arguments ignored.")
        characteristics=[]
        for x in range(9):
            characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        optreplace = DiceBot3.diceRolling("2d10+25")[-2:]
        wounds = DiceBot3.diceRolling("1d5")[0]
        fate = DiceBot3.diceRolling("1d10")[0]
        out = "Characteristic rolls: {}".format(characteristics)
        out += "  Optional replacement roll: {}".format(optreplace)
        out += "  Wounds Roll:  {}".format(wounds)
        out += "  Fate Roll:  {}".format(fate)
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

# #System
@bot.slash_command (
    hidden=True,
    help = """Provides access to internal bot systems, sometimes via password authentication
              UpdateSelf [password]         - access DiceServitor github repo and preform a server-side self update
              SetLogging [password] [level] - set server-side output.log logging level to:  INFO, WARNING, ERROR, CRITICAL, DEBUG.  Default is INFO
              GetVersion                    - return version as shown in config.xml
              GetShard                      - return AWS instance ID, which only works if the bot is running on AWS""",
    brief = "System command.  Can require authentication.")
@commands.has_role('DS-Developer')

async def system(ctx, *args):
    async with ctx.typing():
        try:    
            log.warning("System command invoked with arguments: {}".format(args))
            out = ""
            log.warning(args)
            log.warning("Length of args: {}".format(len(args)))
            if str(args[0]).lower() == "updateself":
                if str(args[1]) == SYS_PASS:
                    log.warning("Update authentication successful.")
                    await ctx.channel.send("Updating server side code...")
                    os.system('./botUpdate.sh')
                else:
                    out += "Self update authentication failed"
            if str(args[0]).lower() == "setlogging":
                log.warning("Authenticating attempt to change logging level...")
                if str(args[1]) == SYS_PASS:
                    log.warning("Authentication successful.")                    
                    out += "Logging level set to {0}".format(str(args[2]))
                    log.Logger.setLevel(log.Logger,str(args[2]))
                else:
                    log.warning("Auth fail.")
                    out += "Authentication failed, logging level unchanged."
            if str(args[0]).lower() == "getversion":
                out += "Dice Servitor version: {}".format(BOT_VERSION)
            if str(args[0]).lower() == "getshard":
                out += subprocess.getoutput('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')
        except Exception as e:
            log.error(e)
            out += "Exception in system: {}".format(e)
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

# #Custom Status
@bot.slash_command (
    hidden=True,
    help = """Set the bot's custom status
              custrole [password] [status]"""
)
@commands.has_role('DS-Developer')

async def custrole(ctx, *args):
    async with ctx.typing():
        try:
            log.warning("Change status command invoked with arguments: {}".format(args))
            out = ""
            log.warning(args)
            log.warning("Length of args: {}".format(len(args)))
            log.warning("Authenticating attempt to change role...")
            if (str(args[0]) == SYS_PASS):
                log.warning("Authentication successful")
                log.warning("Changing custom status...")
                log.warning("Collapsing arguments into status string...")
                i = 1
                tmpargstr = ""
                tmpargs = []
                for arg in args:
                    tmpargs.append(arg)
                tmpargs.pop(0)
                for arg in tmpargs:
                    tmpargstr += "{} ".format(arg)                
                    i += 1
                log.warning("Arguments collapsed into status string.")
                log.warning("Status string: {}".format(tmpargstr))
                activity = discord.Activity(name=tmpargstr, type=discord.ActivityType.watching)                
                await bot.change_presence(activity=activity)
                log.warning("Custom status updated.")
        except Exception as e:
            log.error(e)
            out += "Exception in custrole: {}".format(e)
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

bot.run(DISCORD_TOKEN)