from collections import deque
import discord

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

    def empty(self):
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

    #def remove(self,title:str):
    #    for i in range(len(self.playque)):
    #        if self.playque[i].title == title:
    #            self.remove(i)
    async def embedlist(self,ctx):
        embed=discord.Embed()
        for i in range(len(self.playque)):
            embed.add_field(name="\u200b",
                            value="{}{}. {}".format("" if i != 0 else "▷  ",i+1,self.playque[i].title),
                            inline=False)     
        embed.set_author(name="Playlist: ", icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
        sent_embed = await ctx.send(embed=embed)



    def __str__(self):
        str = ""
        for i in range(len(self.playque)):
            str += ("{}. {}{}".format(i+1,self.playque[i].title,"" if i == len(self.playque)-1 else "\n"))
        return str

