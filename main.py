import discord
import os
#import dice_v2
from xml.dom import minidom
import DiceBot3
from discord.ext import commands

#Read config file
configFile = 'config.xml'
config = minidom.parse(configFile)
BOT_VERSION = config.getElementsByTagName('botVersion')[0].firstChild.data
DISCORD_TOKEN = config.getElementsByTagName('discordToken')[0].firstChild.data
SYS_PASS = config.getElementsByTagName('adminPassword')[0].firstChild.data

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
            print("Roll command invoked with arguments: {}".format(args))
            argument=""
            #Simplify/condense multiple arguments into a single var
            for arg in args:
                argument += arg
            print("Results of argument simplicication: {}".format(argument))
            out = DiceBot3.diceRolling(argument)
            print(out)
            
        except Exception as e:
            print(str(e))
            out = "Unable to parse roll command, please refer to ``!help roll`` for syntax"
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

@bot.command (hidden=True)
@commands.has_role('DS-Developer')

async def system(ctx, *args):
    async with ctx.typing():
        try:    
            print("System command invoked with arguments: {}".format(args))
            out = ""
            print(args)
            print("Length of args: {}".format(len(args)))
            if str(args[0]).lower() == "updateself":
                if str(args[1]) == SYS_PASS:
                    print("Update authentication successful.")
                    out += "Updating server side code..."
                    os.system('./botUpdate.sh')
                else:
                    out += "Self update authentication failed"
            if str(args[0]).lower() == "getversion":
                out += "Dice Servitor version: {}".format(BOT_VERSION)
            if str(args[0]).lower() == "getshard":
                out += os.system('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')
        except Exception as e:
            out += "Exception in system: {}".format(e)
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

bot.run(DISCORD_TOKEN)