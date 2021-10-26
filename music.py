import discord
from discord.ext import commands
import youtube_dl
#from collections import deque

#from string import printable
#import urllib
#import urllib.parse
#import urllib.request
#from bs4 import BeautifulSoup
#from selenium import webdriver

from youtube_search import YoutubeSearch

from utils.songrequest import SongRequest
from utils.playlist import Playlist
from utils.customhelp import CustomHelp

from datetime import datetime

#import os

#import asyncio

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.help_command = CustomHelp()
        #self.client.remove_command('help')
        self.playque = Playlist()

        self.voice_client = None
        self.voice_channel = None
        #self.text_channel = None

        self.last_queue_message = None
        self.last_now_playing = None

        self.loop_song = False

        self.current_song_path = None
        #intended to stopped users from abusing buttons
        #self.last_action = None
        #self.last_user = None

        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 4294', 'options': '-vn'}
        self.YDL_OPTIONS = {'format':"bestaudio",'youtube_include_dash_manifest': False,'quiet': False,'default_search': 'ytsearch'}
            
        self.np_icon = "https://c.tenor.com/GcCv_0rvJlYAAAAC/taiga-circle.gif"
        #"https://m.media-amazon.com/images/G/01/digital/music/player/web/sixteen_frame_equalizer_accent.gif"
        self.np_stopped_icon = "https://c.tenor.com/brz3_pBWenIAAAAC/logo-circle.gif"
        #"https://www.premierhealth.com/Content/images/loading.gif"

        """
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
        """
    
    @commands.command()
    async def ui(self,ctx,*,icon_url):
        self.np_icon=icon_url
        await ctx.message.delete()
        await self._now_playing(ctx)

    @commands.command()
    async def uis(self,ctx,*,icon_url):
        self.np_stopped_icon=icon_url
        await ctx.message.delete()
        await self._now_playing(ctx)
    #test function
    @commands.command()
    async def test(self,ctx):
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

    @commands.Cog.listener()
    async def on_ready(self):
        print("\nBot is online!\n")

    #Joins the author's channel.
    @commands.command()
    async def join(self,ctx):
        author_voice = ctx.author.voice
        if author_voice is None or author_voice.channel is None:
            await ctx.send("You need to be in a voice channel!", delete_after=10.0)
            return False
        #Join their channel
        elif self.voice_client is None:
            self.clear_yt_cache()
            self.voice_client = await author_voice.channel.connect()
            self.voice_channel = author_voice.channel
            return True
        #Not in the same channel.
        elif self.voice_channel != author_voice.channel:
            await ctx.voice_client.move_to(author_voice.channel)
            self.voice_channel = author_voice.channel
            return True
        #await ctx.send("Hello, same channel.")
        return True

    @commands.command(name='quit')
    async def _quit(self,ctx,username=None):
        if self.voice_client is not None:
            await self.voice_client.disconnect()
            #await ctx.send("fUck d@7",delete_after=10000)
            self.voice_client = None
            self.voice_channel = None
            #self.text_channel = None
        self.playque.clear()
        self.loop_song = False
        #self.clear_song_cache()
        await self.delete_last_queue_message()
        await self.delete_last_now_playing()
        if username is None:
            username = ctx.author.name
        print("[{}] {} booted the bot...".format(self.get_time_string(),username))
        #self.que_title.clear()
        #self.que_thumbnail.clear()
        #self.que_author.clear()

    """
    def clear_song_cache(self):
        if self.current_song_path is not None:
            os.remove(self.current_song_path)
        self.current_song_path = None
    """

    def toggle_loop(self,username):
        self.loop_song = not self.loop_song
        if self.loop_song:
            print("[{}] {} looped current song...".format(self.get_time_string(),username))
        else:
            print("[{}] {} unlooped current song...".format(self.get_time_string(),username))
        
    @commands.command(name='pause')
    async def _pause(self,ctx,username=None):
        self.voice_client.pause()
        if username is None:
            username = ctx.author.name
        print("[{}] {} paused...".format(self.get_time_string(),username))
        #await self.text_channel.send("⏸")
    
    @commands.command(name='resume')
    async def _resume(self,ctx,username=None):
        self.voice_client.resume()
        if username is None:
            username = ctx.author.name
        print("[{}] {} resumed...".format(self.get_time_string(),username))
        #await self.text_channel.send("⏯")
      
    @commands.command(name='skip')
    async def _skip(self,ctx,username=None):
        self.loop_song = False
        self.voice_client.stop()
        if username is None:
            username = ctx.author.name
        print("[{}] {} skipped the song...".format(self.get_time_string(),username))
        #await self.text_channel.send("⏭️")
    
    @commands.command(name='stop')
    async def _stop(self,ctx,username=None):
        self.playque.clear()
        self.voice_client.stop()
        self.loop_song = False
        if username is None:
            username = ctx.author.name
        print("[{}] {} stopped playback...".format(self.get_time_string(),username))

    @commands.command(name='remove')
    async def _remove(self,ctx,index:int,username=None):
        #print(self.playque)
        if index > 0 and index < len(self.playque):
            #if index == 0:
            #    return await self.skip(ctx,username)
            removed = self.playque.remove(index)
            if username is None:
                username = ctx.author.name
            print("[{}] {} removed '{}'...".format(self.get_time_string(),username,removed.title))
            try:
                await ctx.message.delete()
                await ctx.send("Removed at slot {} | {}```{}```".format(index,username,removed.title),delete_after=10.0)
            except Exception as e:
                print("[{}] Used trashcan emoji to remove.".format(self.get_time_string()))
            del removed
            await self.update_embed()

    #@commands.command()
    #async def list(self,ctx):
    #    await self.playque.embedlist(ctx)

    @commands.command(name = 'play')
    async def _add_youtube(self,ctx,*,track, quiet=False):
        """Adds the track to the playlist instance and plays it, if it is the first song"""
        if (await self.join(ctx)):
        # If the track is a video title, get the corresponding video link first
            #request = self.convert_to_songrequest(track,ctx.author.name)
            #request = self.track_to_link(track)
            request = self.link_to_songrequest(track,ctx.author.name)
            #print (request.thumbnail)
            if request is None:
                await ctx.send("```No results, try another keyword/link!```",delete_after=10.0)
            else:
                self.playque.add(request)
                print("[{}] {} added '{}'...".format(self.get_time_string(),ctx.author.name,request.title))
                
                try:
                    await ctx.message.delete()
                except Exception as e:
                    print("[{}] No '!play' messages to remove.".format(self.get_time_string()))

                if len(self.playque) == 1:
                    await self.play_link(ctx,request.url)
                    #print("[{}] Playing song: '{}'...".format(self.get_time_string(),self.playque[0].title))
                else:
                    if quiet is False:
                        await self.delete_last_queue_message()
                    #self.last_queue_message = await ctx.send("Queued at slot {}: ```{}```".format(len(self.playque)-1,request.title))
                        self.last_queue_message = await ctx.send("Queued at slot {} | {}```{}```".format(len(self.playque)-1,request.requester,request.title),delete_after=10.0)
                    await self.update_embed()
                    #print("[{}] {} added '{}' to the playlist...".format(self.get_time_string(),ctx.author.name,request.title))
            
                #if not ("watch?v=" in track):
                #    self.last_queue_message = await ctx.send("Queued at slot {}: {}".format(len(self.playque),request.url))
                #else:
                    
                    try:
                        await self.last_queue_message.add_reaction("🗑")
                    except Exception as e:
                        print("[{}] Cannot add reaction.".format(self.get_time_string()))

    def link_to_songrequest(self, title, user):
        #Searches youtube for the video title and returns the first results video link
        #filter(lambda x: x in set(printable), title)
        # Parse the search result page for the first results link
        #query = urllib.parse.quote_plus(title)
        results = YoutubeSearch(title, max_results=5).to_dict()
        #for i in range(len(results)):
        #    print(results[i]['title'])
        #print(results[0])
        if len(results) > 0:
            return SongRequest(title=results[0]['title'],
                                url='https://www.youtube.com' + results[0]['url_suffix'],
                                thumbnail=results[0]['thumbnails'][0], 
                                requester=user,
                                duration=results[0]['duration'],
                                views=results[0]['views'])
    
        return None

    """
    def convert_to_songrequest(self, title, user):
        #Searches youtube for the video title and returns the first results video link
        #print("Pina coladas")
        if  "watch?v=" in title and "&" in title:
        #    print("Pina colada")
            title = title.split("&")[0]
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
                                    requester=user,
                                    #duration=results[checked_videos].find("span",{"id":"text"}),
                                    views=results[checked_videos].find("span",{"class":"style-scope ytd-video-meta-block"}).string)
                #self.que_title.append(results[checked_videos].h3.a['title'])
                #self.que_thumbnail.append(results[checked_videos].div.a.img['src'])
                #self.que_author.append()
                #return 'https://www.youtube.com' + results[checked_videos].h3.a['href']
            checked_videos += 1
        return None
    """

    def clear_yt_cache(self):
        youtube_dl.YoutubeDL().cache.remove()

    async def play_link(self,ctx,url:str):
        if url is None:
            #await self.delete_last_queue_message()
            await self._now_playing(ctx)
            return
        if (await self.join(ctx)):
            if not self.loop_song:
                #await self.delete_last_queue_message()
                await self._now_playing(ctx)

            print("[{}] Playing: {}".format(self.get_time_string(),self.playque[0].title))
            #self.text_channel = ctx.message.channel

        #print (url)
        #    url = self.convert_to_youtube_link(url)
        #print (url)       
            #self.voice_channel.stop()
            with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                
                #self.playque[0].duration = self.seconds_to_duration(info['duration'])
        
                #await self.text_channel.send(url)
                source = await discord.FFmpegOpusAudio.from_probe(url2, **self.FFMPEG_OPTIONS)
                #source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
                self.voice_client.play(source, after=lambda e: self.next_song(ctx,e))
            #self.voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: self.next_song(e))
            #self.voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: self.next_song(e))


    def seconds_to_duration(self,seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return ("{}{}{}{}{}{}".format(hours if hours != 0 else "",
                                     "" if hours == 0 else " hour " if hours == 1 else " hours ",
                                     minutes if minutes != 0 else "",
                                     "" if minutes == 0 else " second " if minutes == 1 else " minutes ",
                                     seconds if seconds != 0 else "",
                                     "" if seconds == 0 else " second" if seconds == 1 else " seconds",
                                     ))

    def next_song(self,ctx,error):
        """Invoked after a song is finished. Plays the next song if there is one, resets the nickname otherwise"""
        next_song = None
        if not self.playque.empty():
            if not self.loop_song:
                #self.clear_song_cache()
                self.playque.popleft()
                #self.que_title.popleft()
                #self.que_thumbnail.popleft()
                #self.que_author = deque()
            if not self.playque.empty():
                next_song = self.playque[0].url
                #print("[{}] Playing song: '{}'...".format(self.get_time_string(),self.playque[0].title))
    
        coro = self.play_link(ctx,next_song)
        self.client.loop.create_task(coro)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        elif reaction.emoji == "🔂" and self.last_now_playing==reaction.message:
            self.toggle_loop(user.name)
        elif reaction.emoji == "⏯" and self.last_now_playing==reaction.message:
            await self._pause(reaction.message.channel,username=user.name)
        elif reaction.emoji == "⏭️" and self.last_now_playing==reaction.message:
            await self._skip(reaction.message.channel,username=user.name)
        elif reaction.emoji == "🛑" and self.last_now_playing==reaction.message:
            await self._stop(reaction.message.channel,username=user.name)
        elif reaction.emoji == "❌" and self.last_now_playing==reaction.message:
            await self._quit(reaction.message.channel,username=user.name)
        
        elif reaction.emoji == "🗑" and self.last_queue_message==reaction.message:
            await self._remove(reaction.message.channel,len(self.playque)-1,username=user.name)
            #await self.update_embed()
            await self.delete_last_queue_message()

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        elif reaction.emoji == "🔂" and self.last_now_playing==reaction.message:
            self.toggle_loop(user.name)
        elif reaction.emoji == "⏯" and self.last_now_playing==reaction.message:
            await self._resume(reaction.message.channel,username=user.name)

    @commands.command(name='song')
    async def _now_playing(self,ctx):
        #### Create the initial embed object ####
        if not self.playque.empty():
            embed=discord.Embed(title="{}".format(self.playque[0].title),
                                description="{} | Requested by {}".format(self.playque[0].duration,self.playque[0].requester), 
                                url=self.playque[0].url, color=0xDCDCDC
                                )
            embed.set_thumbnail(url=self.playque[0].thumbnail)
            if self.playque.has_queue():
                upnext = ""
                for i in range(1,len(self.playque)):
                    upnext += ("\n{}. {}".format(i,self.playque[i].title))
                embed.set_footer(text="Up next: "+upnext)
                #embed.set_footer(text="Up next: \n"+self.playque[1].title)
            else:
                embed.set_footer(text="Up next: empty queue!")
            #embed.set_author(name="Now playing:", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
            embed.set_author(name="Now playing:", icon_url=self.np_icon)
            
            await self.delete_last_now_playing()
            self.last_now_playing = await ctx.send(embed=embed)
            try:
                await self.last_now_playing.add_reaction("🔂")
                await self.last_now_playing.add_reaction("⏯")
                await self.last_now_playing.add_reaction("⏭️")
                await self.last_now_playing.add_reaction("🛑")
            except Exception as e:
                print("[{}] Cannot add reaction.".format(self.get_time_string()))

        else:
            embed=discord.Embed(title="Nothing is currently playing.", color=0xDCDCDC)
            embed.set_author(name="Now playing:", icon_url=self.np_stopped_icon)
            #embed.set_author(name="Now playing:", icon_url="https://m.media-amazon.com/images/G/01/digital/music/player/web/sixteen_frame_equalizer_accent.gif")
            await self.delete_last_now_playing()
            self.last_now_playing = await ctx.send(embed=embed)
            try:
                await self.last_now_playing.add_reaction("❌")
            except Exception as e:
                print("[{}] Cannot add reaction.".format(self.get_time_string()))
        # Add author, thumbnail, fields, and footer to the embed
        #embed.set_thumbnail(url=self.que_thumbnail[0])
        #embed.add_field(name="Up next:", value="Index 0 of title que", inline=False) 
        
        #### Useful ctx variables ####
        ## User's display name in the server
        #ctx.author.display_name

        ## User's avatar URL
        #ctx.author.avatar_url

    async def update_embed(self,ctx = None):
        #### Create the initial embed object ####
        if not self.playque.empty():
            edit=discord.Embed(title="{}".format(self.playque[0].title),
                                description="{} | Requested by {}".format(self.playque[0].duration,self.playque[0].requester), 
                                url=self.playque[0].url, color=0xDCDCDC
                                )

            edit.set_thumbnail(url=self.playque[0].thumbnail)
            if self.playque.has_queue():
                upnext = ""
                for i in range(1,len(self.playque)):
                    upnext += ("\n{}. {}".format(i,self.playque[i].title))
                edit.set_footer(text="Up next: "+upnext)
                #embed.set_footer(text="Up next: \n"+self.playque[1].title)
            else:
                edit.set_footer(text="Up next: empty queue!")
            #edit.set_author(name="Now playing:", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
            edit.set_author(name="Now playing:", icon_url=self.np_icon)#await self.delete_last_now_playing(self.last_now_playing)
            await self.last_now_playing.edit(embed=edit)

    async def delete_last_queue_message(self):
        if self.last_queue_message is not None:
            try:
                await self.last_queue_message.delete()
            except Exception as e:
                print("[{}] Last message is already deleted.".format(self.get_time_string()))
            self.last_queue_message = None

    async def delete_last_now_playing(self):
        if self.last_now_playing is not None:
            try:
                await self.last_now_playing.delete()
            except Exception as e:
                print("[{}] Last message is already deleted.".format(self.get_time_string()))
            self.last_now_playing = None

    @commands.command()
    async def nodat(self,ctx):
        await ctx.send("Dat La is now your Butt Buddy.")


    """
    @commands.command()
    async def search(self,ctx,*,title):
        if not title:
            return
        filter(lambda x: x in set(printable), title)
        query = urllib.parse.quote_plus(title)
        url = "https://www.youtube.com/results?search_query=" + query
        #print("url:" + url)
        self.driver.get(url)     
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        results = soup.findAll("ytd-video-renderer",{"class":"style-scope ytd-item-section-renderer"})

        checked_videos = 0
        video_url_list = []
        embed=discord.Embed()
        #search_results = ""
        while checked_videos < 10 and checked_videos < len(results):
            if "user" not in results[checked_videos].h3.a['href'] and "&list=" not in results[checked_videos].h3.a['href']:
                video_url_list.append('https://www.youtube.com' + results[checked_videos].h3.a['href'])

                embed.add_field(name="\u200b",
                                value="{}. {}".format(checked_videos+1,results[checked_videos].h3.a['title']),
                                inline=False)
                #search_results += "{}. {}\n".format(checked_videos+1,results[checked_videos].h3.a['title'])
            checked_videos += 1
        #embed.set_footer(text=search_results)
        embed.set_author(name="Search results for '{}':".format(title), icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
        sent_embed = await ctx.send(embed=embed)

        for i in range(checked_videos):
            if i == 9:
                try:
                    await sent_embed.add_reaction("🔟")
                except Exception as e:
                    print("[{}] Cannot add reaction.".format(self.get_time_string()))
            else:
                try:
                    await sent_embed.add_reaction("{}\u20e3".format(i+1))
                except Exception as e:
                    print("[{}] Cannot add reaction.".format(self.get_time_string()))
        return video_url_list
    """
    """
    @commands.command()
    async def help(self,ctx):
        
        #### Create the initial embed object ####
        #helpBlock=discord.Embed(title="Commands", color=0xDCDCDC)
        helpBlock=discord.Embed(title="", color=0xDCDCDC)

        # Add author, thumbnail, fields, and footer to the embed
        helpBlock.set_author(name="tonyDeez", icon_url="https://cdn.discordapp.com/avatars/153585708005720065/9728219218ae5a0d0666ed7b52e25190.png")

        helpBlock.set_thumbnail(url="https://cdn.discordapp.com/emojis/880523014071009391.gif?v=1")

        helpBlock.add_field(name="!play <keywords/YouTube link>", value="Plays/queues most relevant video on YouTube.", inline=False) 
        helpBlock.add_field(name="!search <keywords>", value="Looks up top 10 most relevant videos for playback.", inline=False)
        helpBlock.add_field(name="!song", value="Shows now playing.", inline=False)

        helpBlock.add_field(name="!pause", value="⏸", inline=True)
        helpBlock.add_field(name="!resume", value="⏯", inline=True)
        helpBlock.add_field(name="!skip", value="⏭️", inline=True)
        helpBlock.add_field(name="!loop", value="🔂", inline=True)
        helpBlock.add_field(name="!stop", value="🛑", inline=True)
        helpBlock.add_field(name="!quit", value="❌", inline=True)
#helpBlock.add_field(name="!playing", value="Shows now playing.", inline=True)
        helpBlock.add_field(name="!nodat", value="Bar Dat from the party.", inline=True)
        #helpBlock.set_footer(text="List of available controls for the music bot, complain to Dat about functionality or lack thereof.")
        #### Useful ctx variables ####
        ## User's display name in the server
        #ctx.author.display_name

        ## User's avatar URL
        #ctx.author.avatar_url
        await ctx.send(embed=helpBlock)
    """
    def get_time_string(self):
        return datetime.now().strftime("%H:%M:%S")

def setup(client):
    client.add_cog(music(client))