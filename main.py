import asyncio
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
#from mysql.connector import connect, Error
import sqlite3
from sqlite3 import Error


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
SQL_FOLD = readConfig('sqlFolder')
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
if SQL_FOLD != None:
    log.info("SQLite folder path loaded!")
else:
    log.error("SQLite folder path not loaded!")
if DEV_SVID != None:
    log.info("Dev server ID loaded!")
else:
    log.error("Dev server ID not loaded!")
#END Config Checks

log.info("Dice Servitor initialized.")

#bot = commands.Bot(command_prefix="!")
bot = commands.InteractionBot(sync_commands_debug=True)

#Ping
@bot.slash_command(
    help = "Responds with 'pong'!",
    brief = "Responds with 'pong'!"
)
async def ping(ctx):
    await ctx.channel.send("pong")

#Slash Command Timer
# @bot.slash_command()
# async def timer(inter: disnake.ApplicationCommandInteraction, seconds: int):
#     await inter.response.send_message(f"Setting a timer for {seconds} seconds.")
#     await asyncio.sleep(seconds)
#     await inter.followup.send(f"{inter.author.mention}, your timer expired!")

#Slash Command Ping
@bot.slash_command(
    name="sping",
)
async def sping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message("Spong!")

@bot.slash_command( description = "Shows descriptions of commands" )
async def help(inter, command:str):
    async with inter.channel.typing():
        out = ""
        if command.lower() == "roll":
            out = """Rolls dice.  Supports Target Number, +/- modification, and drop lowest.
The command doesn't care about spacing, but any malformed arguments will throw it off. :(
Syntax:  roll 3d10#comment will roll 3 d10 with a comment (use underscores instead of spaces)
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
        if command.lower() == "system":
            out = """Provides access to internal bot systems, sometimes via password authentication
UpdateSelf [password]         - access DiceServitor github repo and preform a server-side self update
SetLogging [password] [level] - set server-side output.log logging level to:  INFO, WARNING, ERROR, CRITICAL, DEBUG.  Default is INFO"""
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
        out = "Characteristic rolls: {}".format(characteristics)
        out += "  Optional replacement roll: {}".format(optreplace)
        out += "  Wounds Roll:  {}".format(wounds)
        out += "  Fate Roll:  {}".format(fate)
        message = str(out)
    await inter.response.send_message(message)

# #System
@bot.slash_command (
        guild_ids=[int(DEV_SVID)],
        hidden=True,
        help = """Provides access to internal bot systems, sometimes via password authentication
                  UpdateSelf [password]         - access DiceServitor github repo and preform a server-side self update
                  SetLogging [password] [level] - set server-side output.log logging level to:  INFO, WARNING, ERROR, CRITICAL, DEBUG.  Default is INFO""",
        brief = "System command.  Can require authentication.")
@commands.has_role('DS-Developer')

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
@bot.slash_command (
        guild_ids=[826534172079554581],
        hidden=True,
        help = """Set the bot's custom status
                  custrole [password] [status]"""
)
@commands.has_role('DS-Developer')

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

def builddbpath(dbidRaw):
    log.info("Building database path...")
    dbpath = os.getcwd()
    dbpath += "\\{}".format(SQL_FOLD)
    if not os.path.exists(dbpath):
        log.info("{} folder does not exist.".format(SQL_FOLD))
        log.info("Creating {} folder...".format(SQL_FOLD))
        os.mkdir(SQL_FOLD)
    dbid = "{}_sheets.sqlite.db".format(dbidRaw)
    dbpath += "\\{}".format(dbid)
    log.info("Database path built: {}".format(dbpath))
    return dbpath

@bot.slash_command(
    hidden=True,
    help = "Initialize a server-specific database"
)

async def initdb(inter):
    async with inter.channel.typing():
        out = ""
        log.info("initdb command invoked by {}({}).".format(inter.author.name,inter.author.id))
        dbpath = builddbpath(inter.guild.id)
        dbid = "{}_sheets.sqlite.db".format(inter.guild.id)
        
        conn = None

        try:
            conn = sqlite3.connect(dbpath)
            log.info("Connected to database {}".format(dbid))
            out += "Database {} created successfully.".format(dbid)
        except Error as e:
            log.error(e)
            out += "Exception in initdb: {}".format(e)
        if conn:
            log.info("Closing database connection.")
            conn.close()
        message = inter.author.mention + " " + str(out)
    await inter.response.send_message(message)   

@bot.slash_command(
    hidden=True,
    help = "Initialize the 'actors' table in a server's database."
)

async def inittable(inter):
    async with inter.channel.typing():
        out = ""
        log.info("inittable command invoked by {}({}).".format(inter.author.name,inter.author.name))
        log.info("Connecting to sqlite database...")
        dbpath = builddbpath(inter.guild.id)
        dbid = "{}_sheets.sqlite.db".format(inter.guild.id)

        tablequery = """
CREATE TABLE actors(
    id integer PRIMARY KEY,
    playerid integer NOT NULL,
    name text NOT NULL,
    weaponSkill integer NOT NULL,
    ballisticSkill integer NOT NULL,
    strength integer NOT NULL,
    toughness integer NOT NULL,
    agility integer NOT NULL,
    intelligence integer NOT NULL,
    perception integer NOT NULL,
    willpower integer NOT NULL,
    fellowship integer NOT NULL
)
"""
        try:
            conn = sqlite3.connect(dbpath)
            log.info("Connected to database {}".format(dbid))
            cursor = conn.cursor()
            log.info("Creating table 'actors'...")
            cursor.execute(tablequery)
        except Error as e:
            log.error(e)
            out = "Error creating table: {}".format(e)
        if conn:
            log.info("Closing database connection.")
            conn.close()
        message = inter.author.mention + " " + str(out)
    await inter.response.send_message(message)

@bot.slash_command (
    help = "Add a character by specifying Name and attributes"
)

async def addcharacter(inter, name:str, weaponskill:int, ballisticskill:int, strength:int, toughness:int, agiilty:int, intelligence:int, perception:int, willpower:int, fellowship:int):
    async with inter.channel.typing():
        log.info("addcharacter command invoked by {}({}) with arguments:  name {} WS {} BS {} STR {} TOU {} AGI {} INT {} PER {} WIL {} FEL {}.".format(inter.author.name,inter.author.id,name, weaponskill,ballisticskill,strength,toughness,agiilty,intelligence,perception,willpower,fellowship))
        out = ""
        dbpath = builddbpath(inter.guild.id)
        dbid = "{}_sheets.sqlite.db".format(inter.guild.id)
        playername = inter.author.name
        playerid = inter.author.id

        actorquerybase = "INSERT INTO actors (playerid, name, weaponSkill, ballisticSkill, strength, toughness, agility, intelligence, perception, willpower, fellowship) VALUES ({}, \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {})"
        
        try:            
            conn = sqlite3.connect(dbpath)
            log.info("Connected to database {}".format(dbid))
            cursor = conn.cursor()
            log.info("Checking to see if player {}({}) has character slots.".format(playername, playerid))
            cursor.execute("SELECT * FROM actors WHERE playerid={}".format(playerid))
            data = cursor.fetchall()
            if len(data)<3:
                log.info("Player {}({}) has character slots.".format(playername, playerid))
            else:                
                raise Error("Player {} has used all available character slots.".format(playername))
            log.info("Checking if character {} exists for player {}({})".format(name, playername, playerid))
            cursor.execute("SELECT * FROM actors WHERE playerid={} AND name=\"{}\"".format(playerid, name))
            data = cursor.fetchall()
            if len(data)>0:
                log.info("Character {} exists for player {}({})".format(name, playername,playerid))                
                raise Error("Character {} exists!  To modify an existing character use /modcharacter".format(name))
            actorquery = actorquerybase.format(playerid, name, weaponskill, ballisticskill, strength, toughness, agiilty, intelligence, perception, willpower, fellowship)
            log.info("Attempting the following SQL query:")
            log.info(actorquery)
            log.info("Executing query...")
            cursor.execute(actorquery)
            conn.commit()
            log.info("Confirming query processed successfully...")
            cursor.execute("SELECT * FROM actors WHERE name=\"{}\"".format(name))
            data = cursor.fetchall()
            validationSet = [name,weaponskill,ballisticskill,strength,toughness,agiilty,intelligence,perception,willpower,fellowship]
            for item in validationSet:
                if item in data[0]:
                    continue
                else:
                    log.error("User input not found after actor creation!")
                    log.error("Query:")
                    log.error("SELECT * FROM actors WHERE name=\"{}\"".format(name))
                    log.error("Output: ")
                    log.error("{}".format(data))
                    log.error("User Input: ")
                    log.error("Name: {} WS: {} BS: {} STR: {} TOU: {} AGI: {} INT: {} PER: {} WIL: {} FEL: {}".format(name,weaponskill,ballisticskill,strength,toughness,agiilty,intelligence,perception,willpower,fellowship))
                    raise Error("Validation error!  Expected data was missing.  See server-side debug log for details.")

            out += "Character entry '{}' created successfully.".format(name)
            log.info(out)            
        except Error as e:
            log.error(e)
            out += "Error creating character entry: {}".format(e)
        if conn:
            log.info("Closing database connection.")
            conn.close()
        message = str(out)
    await inter.response.send_message(message)

@bot.slash_command(
    help = "Retrieve a characteristic from a character whose data is stored and roll against it."
)

async def rollcharacteristic(inter, name:str, attribute:str, modifier:str = None):
    async with inter.channel.typing():
        log.info("rollCharacteristic command invoked by {}({}) with arguments: {}".format(inter.author.name,inter.author.id,str(name + " " + attribute)))
        out = ""
        dbpath = builddbpath(inter.guild.id)
        dbid = "{}_sheets.sqlite.db".format(inter.guild.id)
        allowedCharacteristic = ["weaponSkill","ballisticSkill","strength","toughness","agility","intelligence","perception","willpower","fellowship"]
        actorquerybase = "SELECT {} FROM actors WHERE name=\"{}\""
        #Determine the characteristic data to pull
        try:
            if attribute not in allowedCharacteristic:
                out += "Characteristic unknown: {}".format(attribute)
                raise Error(out)
            actorquery = actorquerybase.format(attribute,name)
            conn = sqlite3.connect(dbpath)
            log.info("Connected to database: {}".format(dbid))
            log.info("Querying database with the following:")
            log.info(actorquery)
            cursor = conn.cursor()
            cursor.execute(actorquery)
            data = cursor.fetchall()
            stat = data[0][0]
            stat = int(stat)
            if not modifier:
                roll = "1d100<={}"
                roll = roll.format(stat)
                rollOut = DiceBot3.diceRolling(roll)
                out = rollOut
            if modifier:
                roll = "1d100<={}"                
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
                out += "Character: {}, Statistic: {}, Modifier: {}".format(name,attribute,modifier) + '\n' + roll + '\n' + str(rollOut)
        except (Exception) as e:
            log.error(e)
            out = "Error: {}".format(e)
        if conn:
            log.info("Closing database connection.")
            conn.close()

        message = str(out)
    await inter.response.send_message(message)

bot.run(DISCORD_TOKEN)