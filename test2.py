
import discord
from discord.ext import commands

prefix = "/"
bot = commands.Bot(prefix)

@bot.event
async def on_ready():
    print("Online")

@bot.command(pass_context = True)
async def say(ctx, *, mg = None):
    last_queue_message = await ctx.send("Said: " + mg, mention_author=True)
    await ctx.send("Deleting...")
    await last_queue_message .delete()

bot.run("ODk1NTEzMjI5MDIxODM5MzYw.YV5prw.oI2Ds5Cq0cjoGAXZCWIFmyvSlxc")