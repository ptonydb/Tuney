import discord
from discord.ext import commands
import music

cogs = [music]

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(bot)

bot.run("ODk1NTEzMjI5MDIxODM5MzYw.YV5prw.2KXyXq5J1U-Gg2nJHnBMfcKN6ec")