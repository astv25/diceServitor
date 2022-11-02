import os
import platform
from re import A
import subprocess
import logging as log
from xml.dom import minidom
import DiceBot3
#import discord
#from discord.ext import commands
import disnake
from disnake.ext import commands
from mysql.connector import connect, Error

#BEGIN Logfile
logFile = 'output.log'
logLevel = log.INFO #Possible values:  INFO,WARNING,ERROR,CRITICAL,DEBUG
log.basicConfig(filename=logFile,level=logLevel)
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
SQL_USER = readConfig('sqlUser')
SQL_PASS = readConfig('sqlPass')
SQL_SERV = readConfig('sqlServ')
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
if SQL_USER !=None:
    log.info("SQL database username loaded from config.")
else:
    log.error("SQL database username not loaded!")
if SQL_PASS !=None:
    log.info("SQL database password loaded from config.")
else:
    log.error("SQL database password not loaded!")
if SQL_SERV != None:
    log.info("SQL server IP/hostname loaded from config.")
else:
    log.error("SQL server IP/hostname not loaded!")
#END Config Checks

log.info("Dice Servitor initialized.")

#bot = commands.Bot(command_prefix="!")
#bot = commands.Bot(command_prefix=commands.when_mentioned)
bot = commands.InteractionBot()

#Ping
@bot.slash_command(
    help = "Responds with 'pong'!",
    brief = "Responds with 'pong'!"
)
async def ping(inter):
    await inter.channel.send("pong")

#Roll
@bot.slash_command(
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
async def roll(inter, args:str):
    async with inter.channel.typing():
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
        message = inter.author.mention + " " + str(out)
    await inter.channel.send(message)

#Rtchargen
@bot.slash_command(
    name = "rtchargen",
    help = """Does the basic rolls for creating a Rogue Trader character all at once.
              Rolls 9x 2d10+25 for characteristics plus an additional, optional replacment
              Rolls 1d5 for wounds
              Rolls 1d10 for fate""",
    description = "Rolls dice for Rogue Trader chargen"
)
async def rtchargen(inter, *args):
    async with inter.channel.typing():
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
        message = inter.author.mention + " " + str(out)
    await inter.channel.send(message)

#System
@bot.slash_command (
    hidden=True,
    help = """Provides access to internal bot systems, sometimes via password authentication
              UpdateSelf [password]         - access DiceServitor github repo and preform a server-side self update
              SetLogging [password] [level] - set server-side output.log logging level to:  INFO, WARNING, ERROR, CRITICAL, DEBUG.  Default is INFO
              GetVersion                    - return version as shown in config.xml
              GetShard                      - return AWS instance ID, which only works if the bot is running on AWS""",
    brief = "System command.  Can require authentication.")
@commands.has_role('DS-Developer')

async def system(inter, *args):
    async with inter.channel.typing():
        try:    
            log.warning("System command invoked with arguments: {}".format(args))
            out = ""
            log.warning(args)
            log.warning("Length of args: {}".format(len(args)))
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
        message = inter.author.mention + " " + str(out)
    await inter.channel.send(message)

#Custom Status
@bot.slash_command (
    hidden=True,
    help = """Set the bot's custom status
              custrole [password] [status]"""
)
@commands.has_role('DS-Developer')

async def custrole(inter, *args):
    async with inter.channel.typing():
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
                activity = disnake.Activity(name=tmpargstr, type=disnake.ActivityType.watching)
                await bot.change_presence(activity=activity)
                log.warning("Custom status updated.")
        except Exception as e:
            log.error(e)
            out += "Exception in custrole: {}".format(e)
        message = inter.author.mention + " " + str(out)
    await inter.channel.send(message)

@bot.slash_command(
    hidden=True,
    help = "Initialize a server-specific database and character sheet table"
)

async def initdb(inter):
    async with inter.channel.typing():
        log.info("initDB command invoked")
        log.info("Connecting to MYSQL backend...")
        dbquerybase = "CREATE DATABASE {}"
        dbid = "{}_sheets"
        dbid = dbid.format(inter.guild.id)
        try:
            with connect(
                host = "localhost",
                user = SQL_USER,
                password = SQL_PASS,
                ) as connection:
                dbquery = dbquerybase.format(dbid)
                with connection.cursor() as cursor:
                    cursor.execute(dbquery)
            out = "Database {} created successfully.".format(dbid)
            log.info(out)
            await inter.channel.send(out)
        except Error as e:
            log.error(e)
            out = "Error creating database."
    await inter.channel.send(out)

@bot.slash_command(
    hidden=True,
    help = "Initialize the 'actors' table in a server's database."
)

async def inittable(inter):
    async with inter.channel.typing():
        log.info("Connecting to MYSQL backend...")
        dbid = "{}_sheets"
        dbid = dbid.format(inter.guild.id)
        tablequery = """
CREATE TABLE actors(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    weaponSkill VARCHAR(3),
    ballisticSkill VARCHAR(3),
    strength VARCHAR(3),
    toughness VARCHAR(3),
    agility VARCHAR(3),
    intelligence VARCHAR(3),
    perception VARCHAR(3),
    willpower VARCHAR(3),
    fellowship VARCHAR(3)
)
"""
        try:
            with connect(
                host = "localhost",
                user = SQL_USER,
                password = SQL_PASS,
                database = dbid,
                ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(tablequery)
            out = "Character sheet table created successfully in database {}".format(dbid)
            log.info(out)
            await inter.channel.send(out)
        except Error as e:
            log.error(e)
            out = "Error creating table."
    await inter.channel.send(out)

@bot.slash_command (
    help = "Add a character by specifying Name and attributes"
)

async def addcharacter(inter, *args):
    async with inter.channel.typing():
        log.info("Connecting to MYSQL backend...")
        out = ""
        dbid = "{}_sheets"
        dbid = dbid.format(inter.guild.id)
        actorquerybase = "INSERT INTO actors (name, weaponSkill, ballisticSkill, strength, toughness, agility, intelligence, perception, willpower, fellowship) VALUES (\"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {})"
        #Sanity check arguments
        try:
            if len(args) < 10:
                out += "Insufficient parameters supplied."
                raise out
            if len(args[0]) > 100:
                out += "Name parameter too long."
                raise Exception(out)
            for a in args[1:]:
                if len(a) > 3:
                    out += "One or more characteristic parameters is too long."
                    raise Exception(out)
            #Sanity check pass
            actorquery = actorquerybase.format(args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],args[8],args[9])
            log.info("Attempting the following SQL query:")
            log.info(actorquery)
            with connect(
                host = "localhost",
                user = SQL_USER,
                password = SQL_PASS,
                database = dbid,
                ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(actorquery)
                    connection.commit()
            out += "Character entry '{}' created successfully.".format(args[0])
            log.info(out)
        except Error as e:
            log.error(e)
            out += "Error creating character entry."
        message = inter.author.mention + " " + str(out)
    await inter.channel.send(message)

@bot.slash_command(
    help = "Retrieve a characteristic from a character whose data is stored and roll against it."
)

async def rollcharacteristic(inter, *args):
    async with inter.channel.typing():
        log.info("rollCharacteristic command invoked with arguments: {}".format(args))
        log.info("Connecting to MYSQL backend...")
        out = ""
        dbid = "{}_sheets"
        dbid = dbid.format(inter.guild.id)
        allowedCharacteristic = ["weaponSkill","ballisticSkill","strength","toughness","agility","intelligence","perception","willpower","fellowship"]
        actorquerybase = "SELECT {} FROM actors WHERE name=\"{}\""
        #Determine the characteristic data to pull
        try:
            if len(args) == 0:
                out += "Not enough arguments provided!  Need character name, characteristic to roll, and optionally a modifier"
                raise Exception(out)
            if len(args) <= 1:
                out += "Not enough arguments provided!  Need character name, characteristic to roll, and optionally a modifier"
                raise Exception(out)
            if args[1] not in allowedCharacteristic:
                out += "Characteristic unknown: {}".format(args[1])
                raise Exception(out)
            actorquery = actorquerybase.format(args[1],args[0])
            log.info("Querying MYSQL database with the following:")
            log.info(actorquery)
            with connect(
                host = "localhost",
                user = SQL_USER,
                password = SQL_PASS,
                database = dbid,
                ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(actorquery)
                    for data in cursor:
                        stat = data[0]
            stat = int(stat)
            if len(args) == 2:
                roll = "1d100<={}"
                roll = roll.format(stat)
                rollOut = DiceBot3.diceRolling(roll)
                out = rollOut
            if len(args) >= 3:
                roll = "1d100<={}"
                modifier = args[2]
                log.info("Parsing modifier: {}".format(modifier))
                log.info("Character at modifier[0]: {}".format(modifier[0]))
                if modifier[0] == "+":
                    log.info("Detected positive modifier")
                    actualModifier = int(modifier[1:])
                    rollMod = stat + actualModifier                    
                elif modifier[0] == "-":
                    log.info("Detected negative modifier")
                    actualModifier = int(modifier[1:])
                    rollMod = stat - actualModifier
                else:
                    out += "Invalid modifier!  Acceptable modifiers are +/-"
                    raise Exception(out)
                roll = roll.format(rollMod)
                rollOut = DiceBot3.diceRolling(roll)
                out = rollOut
        except (Exception) as e:
            log.error(e)
            out = "Error: {}".format(e)

        message = inter.author.mention + " " + str(out)
    await inter.channel.send(message)

bot.run(DISCORD_TOKEN)
