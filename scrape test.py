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

driver = webdriver.Chrome()
driver.get("https://www.youtube.com/watch?v=H5KAQnmTduQ")
soup = BeautifulSoup(driver.page_source, "html.parser")   
print(soup.title.string)
results = soup.findAll("ytd-video-renderer",{"class":"style-scope ytd-item-section-renderer"})
checked_videos = 0;
print("\n\n")
print(results[checked_videos].h3.a['title'])
print("\n\n")
results[checked_videos].a