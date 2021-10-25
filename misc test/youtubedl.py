import youtube_dl
import discord
import os

async def play_link(url:str):

        #self.text_channel = ctx.message.channel

    #print (url)
    #    url = self.convert_to_youtube_link(url)
    #print (url)       
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format':"bestaudio"}
    #self.voice_channel.stop()
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        print(url2)
        os.system(url2.strip())
        #self.playque[0].duration = self.format_duration(info['duration'])
                
        #await self.text_channel.send(url)
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)


play_link("https://www.youtube.com/watch?v=tyU7oQ1O6KA")

