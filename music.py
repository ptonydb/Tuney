import discord
from discord.ext import commands
import youtube_dl
from collections import deque
from string import printable
import urllib
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
#import asyncio

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.playque = deque()
        self.que_title = deque()
        self.que_thumbnail = deque()
        self.que_author = deque()
        self.voice_channel = None
        self.text_channel = None
        self.last_queue_message = None
        self.last_now_playing = None
        option = webdriver.ChromeOptions()
        #option.add_argument('--no-sandbox')
        #option.add_argument('--disable-dev-shm-usage')
        #chrome_prefs = {}
        #option.experimental_options["prefs"] = chrome_prefs
        #chrome_prefs["profile.default_content_settings"] = {"images": 2}
        #chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        self.driver = webdriver.Chrome(chrome_options=option)

        print("Bot started, listening for commands...")

    
    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")
        
        if self.voice_channel is None:
            self.voice_channel  = await ctx.author.voice.channel.connect()
            self.text_channel = ctx.message.channel
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            self.voice_channel  = await ctx.author.voice.channel.connect()
            self.text_channel = ctx.message.channel

    @commands.command()
    async def quit(self,ctx):
        if self.voice_channel is not None:
            await self.voice_channel.disconnect()
            await self.text_channel.send("fUck d@7")
            self.voice_channel = None
            self.text_channel = None
        if self.last_queue_message is not None:
            await self.last_queue_message.delete()
        if self.last_now_playing is not None:
            await self.last_now_playing.delete()
        self.playque.clear()
        self.que_title.clear()
        self.que_thumbnail.clear()
        self.que_author.clear()


    @commands.command()
    async def play(self, ctx,*,track):
        """Adds the track to the playlist instance and plays it, if it is the first song"""

        # If the track is a video title, get the corresponding video link first
        link = self.convert_to_youtube_link(track)
        if not ("watch?v=" in track):
            if self.last_queue_message is not None:
                await self.last_queue_message.delete()
            self.last_queue_message = await ctx.send("Queued: " + link)
        else:
            if self.last_queue_message is not None:
                await self.last_queue_message.delete()
            self.last_queue_message = await ctx.send("Queued: " + self.que_title[-1])
            #self.driver.get(track)     
            #soup = BeautifulSoup(self.driver.page_source, "html.parser")   
            #self.que_title.append(soup.title.string)
            #self.driver.get("data:,")
            #link = track
            #response = urllib.request.urlopen(url)
            #html = response.read()
            #soup = BeautifulSoup(html, "html.parser")
            #self.driver.close()
            
            #results = soup.findAll("a",{"id":"video-title"})
            #thumbs = soup.findAll("img",{"class":"style-scope yt-img-shadow"})
        
        self.playque.append(link)
        if len(self.playque) == 1:
          await self.play_link(ctx,link)

    @commands.command()
    async def h(self,ctx):
        
        #### Create the initial embed object ####
        #helpBlock=discord.Embed(title="Commands", color=0xDCDCDC)
        helpBlock=discord.Embed(title="", color=0xDCDCDC)

        # Add author, thumbnail, fields, and footer to the embed
        helpBlock.set_author(name="tonyDeez", icon_url="https://cdn.discordapp.com/avatars/153585708005720065/9728219218ae5a0d0666ed7b52e25190.png")

        helpBlock.set_thumbnail(url="https://cdn.discordapp.com/emojis/880523014071009391.gif?v=1")

        helpBlock.add_field(name="!play <keywords/YouTube link>", value="Plays a song if the queue is empty, or queues up a song if something is playing.", inline=False) 
        helpBlock.add_field(name="!pause", value="⏸", inline=True)
        helpBlock.add_field(name="!resume", value="⏯", inline=True)
        helpBlock.add_field(name="!skip", value="⏭️", inline=True)
        helpBlock.add_field(name="!h", value="Ayuda plz.", inline=True)
        #helpBlock.add_field(name="!playing", value="Shows now playing.", inline=True)
        helpBlock.add_field(name="!quit", value="Boot le bot.", inline=True)
        helpBlock.add_field(name="!nodat", value="Bar Dat from the party.", inline=True)
        #helpBlock.set_footer(text="List of available controls for the music bot, complain to Dat about functionality or lack thereof.")



        #### Useful ctx variables ####
        ## User's display name in the server
        ctx.author.display_name

        ## User's avatar URL
        #ctx.author.avatar_url
        await ctx.send(embed=helpBlock)
        
    @commands.command()
    async def nodat(self,ctx):
        await ctx.send("Dat La is now your Butt Buddy.")

    @commands.command()
    async def song(self,ctx):

        #### Create the initial embed object ####
        embed=discord.Embed(title=self.que_title[0], url=self.playque[0], color=0xDCDCDC)

        # Add author, thumbnail, fields, and footer to the embed
        embed.set_author(name="Now playing:", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")

        #embed.set_thumbnail(url=self.que_thumbnail[0])

        #embed.add_field(name="Up next:", value="Index 0 of title que", inline=False) 
        if len(self.playque) > 1:
            embed.set_footer(text="Up next: "+self.que_title[1])
        else:
            embed.set_footer(text="Up next: empty queue!")
        #### Useful ctx variables ####
        ## User's display name in the server
        #ctx.author.display_name

        ## User's avatar URL
        #ctx.author.avatar_url
        if self.last_now_playing is not None:
            await self.last_now_playing.delete()
        self.last_now_playing = await self.text_channel.send(embed=embed)


    def next_song(self,error):
        """Invoked after a song is finished. Plays the next song if there is one, resets the nickname otherwise"""
        next_song = None
        if len(self.playque) > 0:
            self.playque.popleft()
            self.que_title.popleft()
            #self.que_thumbnail.popleft()
            #self.que_author = deque()
            if len(self.playque)>0:
                next_song = self.playque[0]

        if next_song is not None:
            coro = self.play_link(None,next_song)
            self.client.loop.create_task(coro)

    async def play_link(self,ctx,url:str):
        if self.voice_channel is None:
            self.voice_channel  = await ctx.author.voice.channel.connect()
            self.text_channel = ctx.message.channel

        #print (url)
        #if not ("watch?v=" in url):
        #    url = self.convert_to_youtube_link(url)
        #print (url)       
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':"bestaudio"}
        #self.voice_channel.stop()
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']

            #await self.text_channel.send(url)
            await self.song(ctx)

            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            self.voice_channel.play(source, after=lambda e: self.next_song(e))
            #self.voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: self.next_song(e))
            #self.voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: self.next_song(e))
    
    @commands.command()
    async def pause(self,ctx):
        self.voice_channel.pause()
        #await self.text_channel.send("⏸")
    
    @commands.command()
    async def resume(self,ctx):
        self.voice_channel.resume()
        #await self.text_channel.send("⏯")
      
    @commands.command()
    async def skip(self,ctx):
        self.voice_channel.stop()
        #await self.text_channel.send("⏭️")

    def convert_to_youtube_link(self, title):
        """Searches youtube for the video title and returns the first results video link"""

        filter(lambda x: x in set(printable), title)

        # Parse the search result page for the first results link
        query = urllib.parse.quote_plus(title)
        url = "https://www.youtube.com/results?search_query=" + query


        self.driver.get(url)     
        soup = BeautifulSoup(self.driver.page_source, "html.parser")   
        #response = urllib.request.urlopen(url)
        #html = response.read()
        #soup = BeautifulSoup(html, "html.parser")
        #self.driver.close()
        
        #results = soup.findAll("a",{"id":"video-title"})
        #thumbs = soup.findAll("img",{"class":"style-scope yt-img-shadow"})
        results = soup.findAll("ytd-video-renderer",{"class":"style-scope ytd-item-section-renderer"})
        checked_videos = 0;
        while len(results) > checked_videos:
            if "user" not in results[checked_videos].h3.a['href'] and "&list=" not in results[checked_videos].h3.a['href']:
                self.que_title.append(results[checked_videos].h3.a['title'])
                #self.que_thumbnail.append(results[checked_videos].div.a.img['src'])
                #self.que_author.append()
                return 'https://www.youtube.com' + results[checked_videos].h3.a['href']
            checked_videos += 1
        return None
    


def setup(client):
    client.add_cog(music(client))