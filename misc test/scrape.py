#import sys
#import os
#current = os.path.dirname(os.path.realpath(__file__))
#parent = os.path.dirname(current)
#sys.path.append(parent)

#from string import printable
#import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.parse
import time

from youtube_search import YoutubeSearch

import youtube_dl


import subprocess 


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
driver = webdriver.Chrome(options=option)


YDL_OPTIONS = {'format':"bestaudio",'youtube_include_dash_manifest': False,'quiet': False,'default_search': 'ytsearch'}
            

def func_test(f,x):
    start_time = time.time()
    print("{} : {}".format(f.__name__,f(x)))
    print("--- %s seconds ---" % (time.time() - start_time))

def selenium(title):
    #Searches youtube for the video title and returns the first results video link

    if  "watch?v=" in title and "&" in title:
    #    print("Pina colada")
        title = title.split("&")[0]
    filter(lambda x: x in set(printable), title)
    # Parse the search result page for the first results link
    query = urllib.parse.quote_plus(title)

    url = "https://www.youtube.com/results?search_query=" + query
    driver.get(url)     
    soup = BeautifulSoup(driver.page_source, "html.parser")   
    results = soup.findAll(attrs={'class': 'yt-simple-endpoint style-scope ytd-video-renderer'})
    checked_videos = 0;
    while len(results) > checked_videos:
        if not "user" in results[checked_videos]['href']:
            return 'https://www.youtube.com' + results[checked_videos]['href']
        checked_videos += 1
    return None

def ytsearch(title):
    #Searches youtube for the video title and returns the first results video link
    #filter(lambda x: x in set(printable), title)
    # Parse the search result page for the first results link
    #query = urllib.parse.quote_plus(title)
    results = YoutubeSearch(title, max_results=5).to_dict()
    #for i in range(len(results)):
    #    print(results[i]['title'])
    print(results[0])
    if len(results) > 0:
        return 'https://www.youtube.com' + results[0]['url_suffix']
    return None

def ytdl_sub(title):
    command=['youtube-dl', 'ytsearch:"' + title+'"', '--get-id']
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout.split()
    if len(result) > 0:
        return 'https://www.youtube.com'+ '/watch?v=' + result[0]
    return None



#query = "184 NOW PLAYING PLAY ALL Ragnarok Online OST / BGM AntAnt"
query = "prozd"
func_test(selenium,query)
func_test(ytsearch,query)
func_test(ytdl_sub,query)



