from collections import deque
import discord
import random

class Playlist:
    """Stores the youtube links of songs to be played and already played and offers basic operation on the queues"""

    def __init__(self):
        # Stores the ytlinks os the songs in queue and the ones already played
        self.playque = deque()

    def __len__(self):
        return len(self.playque)

    def __getitem__(self, index):
        return self.playque[index]

    def add(self, songrequest):
        self.playque.append(songrequest)

    def appendleft(self, songrequest):
        self.playque.appendleft(songrequest)

    def clear(self):
        self.playque.clear()

    def popleft(self):
        return self.playque.popleft()

    def pop(self):
        return self.playque.pop()

    def remove(self,index:int):
        removedSong = None
        if index < len(self.playque):
            removedSong = self.playque[index]
            del self.playque[index]
        return removedSong

    def empty(self):
        if len(self.playque) == 0:
            return True
        else:
            return False
    
    def has_queue(self):
        if len(self.playque) > 1:
            return True
        else:
            return False

    def current_song(self):
        if not self.empty():
            return self.playque[0]
        else:
            return None

    def next_song(self):
        if self.has_queued():
            return self.playque[1]
        else:
            return None

    def insert(self, index, songrequest):
        self.playque.insert(index,songrequest)

    def shuffle(self):
        if not self.empty():
            current = self.popleft()
            self.playque = deque(random.sample(self.playque,len(self)))
            #self.insert(0,current)
            self.appendleft(current)

        

    #def remove(self,title:str):
    #    for i in range(len(self.playque)):
    #        if self.playque[i].title == title:
    #            self.remove(i)
    async def embedlist(self,ctx):
        if not self.empty():
            #embed=discord.Embed()
            embed=discord.Embed(title="```▷ {}```".format(self.current_song().title))
            str = ""
            for i in range(1,len(self.playque)):
                #embed.add_field(name="\u200b",
                #                value="{}{} {}{}".format(i if i != 0 else "```▷ ", "." if i != 0 else "",self.playque[i].title,"" if i != 0 else "```"),
                #                inline=False)
                str += ("\n{}. {}".format(i,self.playque[i].title))
            embed.set_footer(text=str)
            embed.set_author(name="Playlist: ", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
            return await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="```No songs here...```")
            embed.set_author(name="Playlist: ", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
            return await ctx.send(embed=embed)



    def __str__(self):
        str = ""
        for i in range(len(self.playque)):
            str += ("{}. {}{}".format(i+1,self.playque[i].title,"" if i == len(self.playque)-1 else "\n"))
        return str

