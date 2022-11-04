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
#END Config Checks

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
    await inter.response.send_message(message)

# #System
@bot.slash_command (
    hidden=True,
    help = """Provides access to internal bot systems, sometimes via password authentication
              UpdateSelf [password]         - access DiceServitor github repo and preform a server-side self update
              SetLogging [password] [level] - set server-side output.log logging level to:  INFO, WARNING, ERROR, CRITICAL, DEBUG.  Default is INFO""",
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

# #Custom Status
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
        log.info("initdb command invoked.")
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
        log.info("inittable command invoked.")
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
            conn.close()
        message = inter.author.mention + " " + str(out)
    await inter.response.send_message(message)

@bot.slash_command (
    help = "Add a character by specifying Name and attributes"
)

async def addcharacter(inter, name:str, weaponskill:int, ballisticskill:int, strength:int, toughness:int, agiilty:int, intelligence:int, perception:int, willpower:int, fellowship:int):
    async with inter.channel.typing():
        log.info("addcharacter command invoked.")
        out = ""
        dbpath = builddbpath(inter.guild.id)
        dbid = "{}_sheets.sqlite.db".format(inter.guild.id)
        playername = inter.user.name
        playerid = inter.user.id

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
            if len(data)>0:
                log.info("Query processed successfully")
            else:
                raise Error("Character creation query failed:  no data returned for character {}".format(name))
            out += "Character entry '{}' created successfully.".format(name)
            log.info(out)            
        except Error as e:
            log.error(e)
            out += "Error creating character entry: {}".format(e)
        if conn:
            conn.close()
        message = inter.author.mention + " " + str(out)
    await inter.response.send_message(message)

@bot.slash_command(
    help = "Retrieve a characteristic from a character whose data is stored and roll against it."
)

async def rollcharacteristic(inter, name:str, attribute:str):
    async with inter.channel.typing():
        log.info("rollCharacteristic command invoked with arguments")        
        out = ""
        dbpath = builddbpath(inter.guild.id)
        dbid = "{}_sheets.sqlite.db".format(inter.guild.id)
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
