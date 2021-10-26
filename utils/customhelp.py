import discord
from discord.ext import commands

class CustomHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        #### Create the initial embed object ####
        #helpBlock=discord.Embed(title="Commands", color=0xDCDCDC)
        helpBlock=discord.Embed(title="", color=0xDCDCDC)

        # Add author, thumbnail, fields, and footer to the embed
        helpBlock.set_author(name="tonyDeez", icon_url="https://cdn.discordapp.com/avatars/153585708005720065/9728219218ae5a0d0666ed7b52e25190.png")

        helpBlock.set_thumbnail(url="https://cdn.discordapp.com/emojis/880523014071009391.gif?v=1")

        helpBlock.add_field(name="!play <keywords/YouTube link>", value="Plays/queues most relevant video on YouTube.", inline=False) 
        helpBlock.add_field(name="!remove <queue slot number>", value="Deletes 🗑️ a requested song from the playlist.", inline=False)
        #helpBlock.add_field(name="!search <keywords>", value="Looks up top 10 most relevant videos for playback.", inline=False)
        helpBlock.add_field(name="!song", value="Shows now playing.", inline=False)
        #helpBlock.add_field(name="!list", value="Shows playlist queue.", inline=False)
        helpBlock.add_field(name="!pause", value="⏸", inline=True)
        helpBlock.add_field(name="!resume", value="⏯", inline=True)
        helpBlock.add_field(name="!skip", value="⏭️", inline=True)
        helpBlock.add_field(name="!loop", value="🔂", inline=True)
        helpBlock.add_field(name="!stop", value="🛑", inline=True)
        helpBlock.add_field(name="!quit", value="❌", inline=True)
#helpBlock.add_field(name="!playing", value="Shows now playing.", inline=True)
        #helpBlock.add_field(name="!nodat", value="Bar Dat from the party.", inline=True)
        await destination.send(embed=helpBlock)