from config.config import*
import discord
from discord.ext import commands

prefix = "/"
bot = commands.Bot(prefix)

@bot.event
async def on_ready():
    print("Online")

@bot.command(pass_context = True)
async def say(ctx, *, mg = None):
    author = ctx.author
    print(type(author.string))

bot.run(token)