import discord
import os
import subprocess
import logging as log
#import dice_v2
from xml.dom import minidom
import DiceBot3
from discord.ext import commands

#Logfile
logFile = 'output.log'
logLevel = log.DEBUG #Possible values:  INFO,WARNING,ERROR,CRITICAL,DEBUG
log.basicConfig(filename=logFile,level=logLevel)

log.info("Dice Servitor initializing...")

#Read config file
configFile = 'config.xml'
os.chdir('/root/diceServitor')
config = minidom.parse(configFile)
BOT_VERSION = config.getElementsByTagName('botVersion')[0].firstChild.data
DISCORD_TOKEN = config.getElementsByTagName('discordToken')[0].firstChild.data
SYS_PASS = config.getElementsByTagName('adminPassword')[0].firstChild.data

log.info("Dice Servitor initialized.")

bot = commands.Bot(command_prefix="!")

@bot.command(
    help = "Responds with 'pong'!",
    brief = "Responds with 'pong'!"
)
async def ping(ctx):
    await ctx.channel.send("pong")

@bot.command(
    help = """Rolls dice.  Supports Target Number, +/- modification, and drop lowest.
              The command doesn't care about spacing, but any malformed arguments will throw it off. :(
              Syntax:  roll 3d10#comment will roll 3 d10 with a comment (use underscores instead of spaces)
                       roll 3d10+5       will roll 3 d10 and add 5 (Other supported math symbols include '-', '*', '/'.
                                         Please note pemdas is not implemented. Use mdas as the input format)
                       roll 1d100<=45    will roll 1 d100 and report each degree of success or failure for a roll <=45
                       roll 1d100>=45    will roll 1 d100 and report each degree of success or failure for a roll >=45
                       roll 1d100<45     will roll 1 d100 and report each degree of success or failure for a roll <45
                       roll 1d100>45     will roll 1 d100 and report each degree of success or failure for a roll >45                        
                       roll 3d10dl2      will roll 3 d10 and remove the lowest 2 die.""",
    brief = "Rolls dice"
)
async def roll(ctx, *args):
    async with ctx.typing():
        try:
            log.info("Roll command invoked with arguments: {}".format(args))
            argument=""
            #Simplify/condense multiple arguments into a single var
            for arg in args:
                argument += arg
            log.info("Results of argument simplicication: {}".format(argument))
            out = DiceBot3.diceRolling(argument)
            print(out)
            
        except Exception as e:
            log.error(str(e))
            out = "Unable to parse roll command, please refer to ``!help roll`` for syntax"
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

@bot.command(
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
        #EXTREME LAZINESS INCOMING
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
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
@bot.command (hidden=True)
@commands.has_role('DS-Developer')

async def system(ctx, *args):
    async with ctx.typing():
        try:    
            log.debug("System command invoked with arguments: {}".format(args))
            out = ""
            log.debug(args)
            log.debug("Length of args: {}".format(len(args)))
            if str(args[0]).lower() == "updateself":
                if str(args[1]) == SYS_PASS:
                    log.debug("Update authentication successful.")
                    await ctx.channel.send("Updating server side code...")
                    os.system('./botUpdate.sh')
                else:
                    out += "Self update authentication failed"
            if str(args[0]).lower() == "getversion":
                out += "Dice Servitor version: {}".format(BOT_VERSION)
            if str(args[0]).lower() == "getshard":
                out += subprocess.getoutput('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')
        except Exception as e:
            out += "Exception in system: {}".format(e)
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

bot.run(DISCORD_TOKEN)