import sqlite3
from sqlite3 import Error

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