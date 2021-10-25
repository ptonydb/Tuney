from string import printable
from utils.songrequest import SongRequest
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib
import urllib.parse
import discord


class SongSearch(driver=None):
    def __init__(self):
        self.results = []
        self.driver = None
        if driver is None:
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
        else:
            self.driver = driver
        self.embed_results = None

    def __getitem__(self, index):
        return self.results[index]

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
        self.embed_results=discord.Embed()
        #search_results = ""
        while checked_videos < 10 and checked_videos < len(results):
            if "user" not in results[checked_videos].h3.a['href'] and "&list=" not in results[checked_videos].h3.a['href']:
                self.results.append('https://www.youtube.com' + results[checked_videos].h3.a['href'])

                self.embed_results.add_field(name="\u200b",
                                value="{}. {}".format(checked_videos+1,results[checked_videos].h3.a['title']),
                                inline=False)
                #search_results += "{}. {}\n".format(checked_videos+1,results[checked_videos].h3.a['title'])
            checked_videos += 1
        #embed.set_footer(text=search_results)
        self.embed_results.set_author(name="Search results for '{}':".format(title), icon_url="https://www.clipartmax.com/png/middle/162-1627126_we-cook-the-beat-music-blue-icon-png.png")
        sent_embed = await ctx.send(embed=self.embed_results)

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
        #return video_url_list
        