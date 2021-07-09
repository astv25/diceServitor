import discord
import os
import dice_v2
import DiceBot3
from discord.ext import commands
DISCORD_TOKEN = 'ODI2NTMzNTA3MDM5MTAwOTY4.YGN3UA.ZbO32L6Gxd1u5W1KznMhlBkqCIc'

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
                       roll 3d10+5      will roll 3 d10 and add 5
                       roll 3d10-5      will roll 3 d10 and subtract 5
                       roll 1d100tn45   will roll 1 d100 and report each degree of success or failure for a roll <=45
                       roll 1d100tn+45  will roll 1 d100 and report each degree of success or failure for a roll >=45
                       roll 1d100tn-45  will roll 1 d100 and report each degree of success or failure for a roll <=45                       
                       roll 3d10r2      will roll 3 d10 and remove the lowest 2 die.""",
    brief = "Rolls dice, retard"
)
async def roll(ctx, *args):
    async with ctx.typing():
        try:
            print("Roll command invoked")
            #Simplify/condense multiple arguments into a single var
            out = DiceBot3.diceRolling(args)
            
        except Exception as e:
            print(str(e))
            out = "Unable to parse roll command, please refer to ``!help roll`` for syntax"
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)

@bot.command(
    help = """Does basic mathematics.
              The command is spacing agnostic, but reacts badly to malformed commands.              
              Syntax:  math 3+5    will add 3 and 5
                       math 3*5    will multiply 3 and 5
                       math 3/5    will divide 3 by 5
                       math 5%3    will find the modulus of 5 and 3
           """,
    brief = "Does math, retard."
)
async def math(ctx, *args):
    async with ctx.typing():
        try:
            print("Math command invoked")
            #Simplify/condense multiple arguments into a single var
            arguments = ""
            if(len(args)>1):
                for each in args:
                    arguments+=str(each).lower()
            else:
                arguments = args[0]
            print("Result of argument simplification: {}".format(arguments))
            out = eval(arguments)
        except Exception as e:
            print(str(e))
            out = "Unable to parse command, please try again."
        message = ctx.author.mention + " " + str(out)
    await ctx.channel.send(message)



bot.run(DISCORD_TOKEN)
