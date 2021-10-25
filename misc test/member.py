import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from config.config import*
import discord
from discord.ext import commands

prefix = "/"
bot = commands.Bot(prefix)
message = None

@bot.event
async def on_ready():
    print("Online")

@bot.command(pass_context = True)
async def say(ctx, *, mg = None):
    #author = ctx.author.name
    global message 
    message = await ctx.send(mg)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    elif reaction.emoji == "🔂" and message==reaction.message:
        print("Same.")
    else:
        print("Not the same.")

bot.run(token)