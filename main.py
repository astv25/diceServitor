import discord
import os
import dice_v2
import DiceBot3
from discord.ext import commands
tokenfile="botToken.txt"
adminFile="adminPW.txt"
f = open(tokenfile,"r")
DISCORD_TOKEN = f.read()
f.close()
f = open(adminFile,"r")
SYS_PASS = f.read()
f.close()

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
              Syntax:  roll 3d10        will roll 3 d10
                       roll 3d10+5      will roll 3 d10 and add 5 (Other supported math symbols include '-', '*', '/'.
                                        Please note pemdas is not implemented. Use mdas as the input format)
                       roll 1d100<=45   will roll 1 d100 and report each degree of success or failure for a roll <=45
                       roll 1d100>=45  will roll 1 d100 and report each degree of success or failure for a roll >=45
                       roll 1d100<45  will roll 1 d100 and report each degree of success or failure for a roll <45
                       roll 1d100>45  will roll 1 d100 and report each degree of success or failure for a roll >45                        
                       roll 3d10dl2      will roll 3 d10 and remove the lowest 2 die.""",
    brief = "Rolls dice, retard"
)
async def roll(ctx, *args):
    async with ctx.typing():
        try:
            print("Roll command invoked")
            argument=""
            #Simplify/condense multiple arguments into a single var
            for arg in args:
                argument += arg
            out = DiceBot3.diceRolling(argument)
            print(out)
            
        except Exception as e:
            print(str(e))
            out = "Unable to parse roll command, please refer to ``!help roll`` for syntax"
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

@bot.command ()
async def updateself(ctx, *args):
    async with ctx.typing():
        print("Self update command invoked.")
        out = ""
        print(args)
        print("Length of args: {}".format(len(args)))
        if str(args[0]) == SYS_PASS:
            print("Update authentication successful.")
            out = "Updating server side code..."
            os.system('./botUpdate.sh')
        else:
            out = "Auth failed"
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

bot.run(DISCORD_TOKEN)
