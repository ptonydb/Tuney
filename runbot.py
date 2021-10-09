from discord.ext import commands
from config.config import *
import discord
import music

def main():
    cogs = [music]
    bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
    for i in range(len(cogs)):
        cogs[i].setup(bot)
    bot.run(token)

if __name__ == "__main__":
    main()