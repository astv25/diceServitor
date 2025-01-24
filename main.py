import os
import platform
import logging as log
from xml.dom import minidom
import DiceBot3
from datetime import datetime
from time import mktime

import disnake
from disnake.ext import commands

#BEGIN Logfile
logFile = 'output.log'
logLevel = log.INFO #Possible values:  INFO,WARNING,ERROR,CRITICAL,DEBUG
log.basicConfig(
    filename=logFile,
    format='%(asctime)s %(levelname)-8s %(message)s',    
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logLevel,
    force=True
    )
#END Logfile

log.info("Dice Servitor initializing...")

#BEGIN Config File
configFile = 'config.xml'

def readConfig(element):
    return config.getElementsByTagName(element)[0].firstChild.data

if platform.system() == 'Linux':
    os.chdir('/root/diceServitor')
config = minidom.parse(configFile)
DISCORD_TOKEN = readConfig('discordToken')
SYS_PASS = readConfig('adminPassword')
DEV_SVID = readConfig('devServerID')
#END Config File

#BEGIN Config Checks
if DISCORD_TOKEN != None:
    log.info("Token loaded from config.")
else:
    log.error("Token not loaded!")
if SYS_PASS != None:
    log.info("System password loaded from config.")
else:
    log.error("System password not loaded!")
if DEV_SVID != None:
    log.info("Dev server ID loaded!")
else:
    log.info("Dev server ID not loaded!")
#END Config Checks

log.info("Dice Servitor initialized.")

#bot = commands.Bot(command_prefix="!")
bot = commands.InteractionBot(sync_commands_debug=True)

#Slash Command Ping
@bot.slash_command(
    name="ping",
)
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message("Pong!")

@bot.slash_command( description = "Shows descriptions of commands" )
async def help(inter, command:str):
    async with inter.channel.typing():
        out = "Command {} does not have help text, sorry".format(command)
        if command.lower() == "roll":
            out = """Rolls dice.  Supports Target Number, +/- modification, and drop lowest.  There's an optional comment field.
The command doesn't care about spacing, but any malformed arguments will throw it off. :(
Syntax:  
roll 3d10         will roll 3 d10
roll 3d10+5       will roll 3 d10 and add 5 (Other supported math symbols include '-', '*', '/'.
                  Please note pemdas is not implemented. Use mdas as the input format)
roll 1d100<=45    will roll 1 d100 and report each degree of success or failure for a roll <=45
roll 1d100>=45    will roll 1 d100 and report each degree of success or failure for a roll >=45
roll 1d100<45     will roll 1 d100 and report each degree of success or failure for a roll <45
roll 1d100>45     will roll 1 d100 and report each degree of success or failure for a roll >45                        
roll 3d10dl2      will roll 3 d10 and remove the lowest 2 die."""
        if command.lower() == "rtchargen":
            out = """Does the basic rolls for creating a Rogue Trader character all at once.
Rolls 9x 2d10+25 for characteristics plus an additional, optional replacment
Rolls 1d5 for wounds
Rolls 1d10 for fate"""
        if command.lower() == "timecode":
            out = """Generate an epoch timecode with a given 24 hr time, date in MM/DD/YYYY"""
        if command.lower() == "system":
            out = """Provides access to internal bot systems, sometimes via password authentication
UpdateSelf [password]         - access DiceServitor github repo and preform a server-side self update
SetLogging [password] [level] - set server-side output.log logging level to:  INFO, WARNING, ERROR, CRITICAL, DEBUG.  Default is INFO"""
        if command.lower() == "custrole":
            out =  """Set the bot's custom status
custrole [password] [status]"""
        await inter.response.send_message(inter.author.mention + " " + out)

#Roll
@bot.slash_command(
        description = "Rolls dice, see help for syntax",
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
async def roll(inter, roll:str, comment:str = None):
    async with inter.channel.typing():
        try:
            if not comment == None: log.info("Roll command invoked by {}({}) with arguments: {}".format(inter.author.name,inter.author.id,roll + " " + comment))
            else: log.info("Roll command invoked by {}({}) with arguments: {}".format(inter.author.name,inter.author.id,roll))
            out = DiceBot3.diceRolling(roll)
            log.info(out)            
            
        except Exception as e:
            log.error(str(e))
            out = "Unable to parse roll command, please refer to ``/help roll`` for syntax"
        #message = inter.author.mention + " " + str(out)
        message = "{} Request: ``{}`` Result: ``{}``".format(inter.author.mention, roll, out)
        if not comment == None: message += " Comment: ``{}``".format(comment)
    await inter.response.send_message(message)

# #Rtchargen
@bot.slash_command(
        help = """Does the basic rolls for creating a Rogue Trader character all at once.
                  Rolls 9x 2d10+25 for characteristics plus an additional, optional replacment
                  Rolls 1d5 for wounds
                  Rolls 1d10 for fate""",
        description = "Rolls dice for Rogue Trader chargen"
)
async def rtchargen(inter):
    async with inter.channel.typing():
        log.info("Character generation command invoked by {}({})".format(inter.author.name,inter.author.id))
        characteristics=[]
        for x in range(9):
            characteristics.append(DiceBot3.diceRolling("2d10+25")[-2:])
        optreplace = DiceBot3.diceRolling("2d10+25")[-2:]
        wounds = DiceBot3.diceRolling("1d5")[0]
        fate = DiceBot3.diceRolling("1d10")[0]
        out = "Characteristic rolls: ``{}``".format(characteristics)
        out += "  Optional replacement roll: ``{}``".format(optreplace)
        out += "  Wounds Roll:  ``{}``".format(wounds)
        out += "  Fate Roll:  ``{}``".format(fate)
        message = str(out)
    await inter.response.send_message(message)

#Owchargen
@bot.slash_command(
        help = """Does the basic rolls for creating an Only War character all at once.
                  Rolls 9x 2d10+20 for characteristics plus an additional, optional replacment
                  Rolls 1d5 for wounds
                  Rolls 1d10 for fate""",
        description = "Rolls dice for Only War chargen"
)
async def owchargen(inter):
    async with inter.channel.typing():
        log.info("Character generation command invoked by {}({})".format(inter.author.name,inter.author.id))
        characteristics=[]
        for x in range(9):
            characteristics.append(DiceBot3.diceRolling("2d10+20")[-2:])
        optreplace = DiceBot3.diceRolling("2d10+20")[-2:]
        wounds = DiceBot3.diceRolling("1d5")[0]
        fate = DiceBot3.diceRolling("1d10")[0]
        out = "Characteristic rolls: ``{}``".format(characteristics)
        out += "  Optional replacement roll: ``{}``".format(optreplace)
        out += "  Wounds Roll:  ``{}``".format(wounds)
        out += "  Fate Roll:  ``{}``".format(fate)
        message = str(out)
    await inter.response.send_message(message)

#SoSRoll
@bot.slash_command(
        help = """Rolls dice with a tn and counts successes""",
        description= "Rolls dice with a tn and counts successes"
)
async def sosroll(inter, numdice:int, tn:int):
    async with inter.channel.typing():
        log.info("SoS Roll command invoked by {}({})".format(inter.author.name,inter.author.id))
        rolls = DiceBot3.diceRolling(str(numdice)+"d10")
        successes = 0
        for die in rolls:
            if (die >= tn):
                successes += 1
        out = "Dice rolls: ``{}``".format(rolls)
        out += " Successes: ``{}``".format(successes)
        message = str(out)
    await inter.response.send_message(message)

# #Generate epoch timecode
@bot.slash_command(
        help = """Generate an epoch timecode with a given 24hr time in HH:MM:SS, date in MM/DD/YYYY""",
        description = "Generate an epoch timecode"
)
async def timecode(inter, time:str, date:str):
    async with inter.channel.typing():
        log.info("Timecode command invoked by {}({})".format(inter.author.name,inter.author.id))
        try:
            dt = datetime.strptime("{} {}".format(time, date), "%H:%M:%S %m/%d/%Y")
            epochtime = int(mktime(dt.timetuple()))
            out = "{} \<t:{}:R\>".format(inter.author.mention, epochtime)
        except Exception as e:
            log.error(str(e))
            out = str(e)
    await inter.response.send_message(out)

# #System
@bot.slash_command(
        dm_permission=False,
        guild_ids=[int(DEV_SVID)],
        help = """Provides access to internal bot systems, sometimes via password authentication
                  UpdateSelf [password]         - access DiceServitor github repo and preform a server-side self update
                  SetLogging [password] [level] - set server-side output.log logging level to:  INFO, WARNING, ERROR, CRITICAL, DEBUG.  Default is INFO""",
        description = "System command.  Can require authentication.")

async def system(inter, argument:str):
    async with inter.channel.typing():
        args = argument.split(' ')
        out = ""
        try:    
            log.warning("System command invoked by {}({}) with arguments: {}".format(inter.author.name,inter.author.id,args))            
            if inter.guild.id != int(DEV_SVID):
                raise Exception("System command received from unauthorized server!")            
            if str(args[0]).lower() == "updateself":
                if str(args[1]) == SYS_PASS:
                    log.warning("Update authentication successful.")
                    await inter.channel.send("Updating server side code...")
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
        except Exception as e:
            log.error(e)
            out += "Exception in system: {}".format(e)
        message = str(out)
    await inter.response.send_message(message)

# #Custom Status
@bot.slash_command(
        dm_permission=False,
        guild_ids=[int(DEV_SVID)],
        help = """Set the bot's custom status
                  custrole [password] [status]""",
        description = "Set a custom status for the bot."
)

async def custrole(inter, argument:str):
    async with inter.channel.typing():
        args = argument.split(' ')
        try:
            log.warning("Change status command invoked by {}({}) with arguments: {}".format(inter.author.name,inter.author.id,args))
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
                activity = disnake.Activity(name=tmpargstr, type=disnake.ActivityType.watching)
                await bot.change_presence(activity=activity)
                log.warning("Custom status updated.")
        except Exception as e:
            log.error(e)
            out += "Exception in custrole: {}".format(e)
        message = inter.author.mention + " " + str(out)
    await inter.response.send_message(message)

bot.run(DISCORD_TOKEN)