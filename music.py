import discord
from discord.ext import commands
import youtube_dl
#from collections import deque
from string import printable
import urllib
import urllib.parse
#import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from songrequest import SongRequest
from playlist import Playlist
#import asyncio

class music(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.playque = Playlist()
        #self.que_title = deque()
        #self.que_thumbnail = deque()
        #self.que_author = deque()

        self.voice_client = None
        self.voice_channel = None
        #self.text_channel = None

        self.last_queue_message = None
        self.last_now_playing = None

        self.loop_song = False

        #intended to stopped users from abusing buttons
        #self.last_action = None
        #self.last_user = None
        
        option = webdriver.ChromeOptions()
        option.add_argument('log-level=2')
        option.add_argument('--headless')
        #option.add_argument('--disable-gpu')
        #option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')
        chrome_prefs = {}
        option.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        self.driver = webdriver.Chrome(chrome_options=option)

        #print("\n\nBot started, listening for commands...\n\n")

    #Joins the author's channel.
    @commands.command()
    async def join(self,ctx):
        author_voice_channel = ctx.author.voice.channel
        if author_voice_channel is None:
            await ctx.send("You need to be in a voice channel!")
            return False
        elif self.voice_client is None:
            self.voice_client = await author_voice_channel.connect()
            self.voice_channel = author_voice_channel
            return True
        #Not in the same channel.
        elif self.voice_channel != author_voice_channel:
            await ctx.voice_client.move_to(author_voice_channel)
            self.voice_channel = author_voice_channel
            return True
        #await ctx.send("Hello, same channel.")
        return True

    @commands.command()
    async def pc(self,ctx):
        userVoiceChannel = ctx.author.voice;
        botVoiceChannel = ctx.guild.me.voice;
        if botVoiceChannel and botVoiceChannel.channel is None:
            return await ctx.send("The bot is not in a voice channel.")
        if userVoiceChannel and userVoiceChannel.channel is None:
            return await ctx.send("You need to be in a voice channel.")
        #print(dir(botVoiceChannel))
        if botVoiceChannel.channel.id != userVoiceChannel.channel.id:
            return await ctx.send("You need to be in the same channel as the bot.")
        await ctx.send("Same channel boys.");
        return True

    @commands.command()
    async def quit(self,ctx):
        if self.voice_client is not None:
            await self.voice_client.disconnect()
            #await ctx.send("fUck d@7",delete_after=10000)
            self.voice_client = None
            self.voice_channel = None
            #self.text_channel = None
        self.playque.empty()
        await self.delete_last_queue_message()
        await self.delete_last_now_playing()
        print("Quitting...")
        #self.que_title.clear()
        #self.que_thumbnail.clear()
        #self.que_author.clear()

    def toggle_loop(self):
        self.loop_song = not self.loop_song
        if self.loop_song:
            print("Looping current song...")
        else:
            print("Not looping current song...")

    @commands.command()
    async def play(self,ctx,*,track):
        """Adds the track to the playlist instance and plays it, if it is the first song"""
        if (await self.join(ctx)):
        # If the track is a video title, get the corresponding video link first
            request = self.convert_to_songrequest(track)
            request.requester = ctx.author.name
            self.playque.add(request)
            await self.delete_last_queue_message()
            if not ("watch?v=" in track):
                self.last_queue_message = await ctx.send("Queued at slot {}: {}".format(len(self.playque),request.url))
            else:
                self.last_queue_message = await ctx.send("Queued at slot {}: {}".format(len(self.playque),request.title))
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
            

            if len(self.playque) == 1:
                await self.play_link(ctx,request.url)
            else:
                await self.song(ctx)

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
        #ctx.author.display_name

        ## User's avatar URL
        #ctx.author.avatar_url
        await ctx.send(embed=helpBlock)
        
    @commands.command()
    async def nodat(self,ctx):
        await ctx.send("Dat La is now your Butt Buddy.")

    @commands.command()
    async def song(self,ctx):

        #### Create the initial embed object ####
        if len(self.playque) != 0:
            embed=discord.Embed(title=self.playque[0].title,
                                description="Requested by {}, {}".format(self.playque[0].requester,self.playque[0].views), 
                                url=self.playque[0].url, color=0xDCDCDC)
            embed.set_thumbnail(url=self.playque[0].thumbnail)
            if len(self.playque) > 1:
                embed.set_footer(text="Up next: "+self.playque[1].title)
            else:
                embed.set_footer(text="Up next: empty queue!")
            embed.set_author(name="Now playing:", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
            await self.delete_last_now_playing()
            self.last_now_playing = await ctx.send(embed=embed)
            await self.last_now_playing.add_reaction("🔂")
            await self.last_now_playing.add_reaction("⏯")
            await self.last_now_playing.add_reaction("⏭️")
            await self.last_now_playing.add_reaction("🛑")
        else:
            embed=discord.Embed(title="Nothing is currently playing.", color=0xDCDCDC)
            embed.set_author(name="Now playing:", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
            await self.delete_last_now_playing()
            self.last_now_playing = await ctx.send(embed=embed)
            await self.last_now_playing.add_reaction("❌")
        # Add author, thumbnail, fields, and footer to the embed
        #embed.set_thumbnail(url=self.que_thumbnail[0])
        #embed.add_field(name="Up next:", value="Index 0 of title que", inline=False) 
        
        #### Useful ctx variables ####
        ## User's display name in the server
        #ctx.author.display_name

        ## User's avatar URL
        #ctx.author.avatar_url


    @commands.Cog.listener()
    async def on_ready(self):
        print("\nBot is ready!\n")
        
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        elif reaction.emoji == "🔂":
            self.toggle_loop()
        elif reaction.emoji == "⏭️":
            await self.skip(None)
        elif reaction.emoji == "⏯":
            await self.pause(None)
        elif reaction.emoji == "🛑":
            await self.stop(None)
        elif reaction.emoji == "❌":
            await self.quit(None)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        elif reaction.emoji == "🔂":
            self.toggle_loop()
        elif reaction.emoji == "⏯":
            await self.resume(None)

    async def delete_last_queue_message(self):
        if self.last_queue_message is not None:
            await self.last_queue_message.delete()
            self.last_queue_message = None

    async def delete_last_now_playing(self):
        if self.last_now_playing is not None:
            await self.last_now_playing.delete()
            self.last_now_playing = None

    def next_song(self,ctx,error):
        """Invoked after a song is finished. Plays the next song if there is one, resets the nickname otherwise"""
        next_song = None
        if len(self.playque) > 0:
            if not self.loop_song:
                self.playque.popleft()
                #self.que_title.popleft()
                #self.que_thumbnail.popleft()
                #self.que_author = deque()
            if len(self.playque)>0:
                next_song = self.playque[0].url
                print("Playing..." + self.playque[0].title)
        #if next_song is not None:
        coro = self.play_link(ctx,next_song)
        self.client.loop.create_task(coro)
        #else:
        #    coro = self.song(ctx)
        #    self.client.loop.create_task(coro)

    async def play_link(self,ctx,url:str):
        if not self.loop_song:
            await self.song(ctx)
        if url is None:
            return
        if (await self.join(ctx)):
            #self.text_channel = ctx.message.channel

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

                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                self.voice_client.play(source, after=lambda e: self.next_song(ctx,e))
            #self.voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: self.next_song(e))
            #self.voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: self.next_song(e))
    
    @commands.command()
    async def pause(self,ctx):
        self.voice_client.pause()
        print("Paused...")
        #await self.text_channel.send("⏸")
    
    @commands.command()
    async def resume(self,ctx):
        self.voice_client.resume()
        print("Unpaused...")
        #await self.text_channel.send("⏯")
      
    @commands.command()
    async def skip(self,ctx):
        self.loop_song = False
        self.voice_client.stop()
        print("Skipped...")
        #await self.text_channel.send("⏭️")
    
    @commands.command()
    async def stop(self,ctx):
        self.playque.empty()
        self.voice_client.stop()
        print("Stopped and cleared queue...")

    def convert_to_songrequest(self, title):
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
                return SongRequest(title=results[checked_videos].h3.a['title'],
                                    url='https://www.youtube.com' + results[checked_videos].h3.a['href'],
                                    thumbnail=results[checked_videos].find("img",{"class":"style-scope yt-img-shadow"})['src'], 
                                    #duration=results[checked_videos].find("span",{"id":"text"}),
                                    views=results[checked_videos].find("span",{"class":"style-scope ytd-video-meta-block"}).string)
                #self.que_title.append(results[checked_videos].h3.a['title'])
                #self.que_thumbnail.append(results[checked_videos].div.a.img['src'])
                #self.que_author.append()
                #return 'https://www.youtube.com' + results[checked_videos].h3.a['href']
            checked_videos += 1
        return None
    


def setup(client):
    client.add_cog(music(client))