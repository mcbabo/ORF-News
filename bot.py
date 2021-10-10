from lxml import html
import requests
import discord
from discord.ext import commands
from discord_slash import SlashCommand
import json
import asyncio
import contextlib
import io
import math

TOKEN = "YOUR_TOKEN"

def get_prefix(bot, message):
    with open("prefix.json", "r") as f:
        prefixes = json.load(f)
    
    return prefixes[str(message.guild.id)]

  
def get_config(name):
    with open("config.json", "r") as f:
        json_file = json.load(f)
    return json_file[name]

  
def get_channels():
    with open("channels.json", "r") as f:
        channels = json.load(f)
    return channels['channels']

  
bot = commands.Bot(command_prefix = "+", help_command = None)


@bot.event
async def on_guild_join(guild):
    with open("prefix.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes[str(guild.id)] = "~"
    
    with open("prefix.json", "w") as f:
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_guild_remove(guild):
    with open("prefix.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes.pop(str(guild.id))
    
    with open("prefix.json", "w") as f:
        json.dump(prefixes, f, indent=4)
        
@bot.command()
async def changeprefix(ctx, prefix):
    with open("prefix.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes[str(ctx.guild.id)] = prefix
    
    with open("prefix.json", "w") as f:
        json.dump(prefixes, f, indent=4)


@bot.command()
async def addChannel(ctx, channel):
    try:
        currentChannels = get_channels()
        currentChannels.append(channel)
        with open("channels.json", "w", encoding="utf8") as f:
            f.write(json.pop({"channels":currentChannels}, indent=4))
        await ctx.send("**Channel removed successfully**")
    except Exception as e:
        await ctx.send(e)
        

@bot.command()
async def removeChannel(ctx, channel):
    try:
        if channel not in get_channels():
            await ctx.send("**Channel not in List**")
            return
        currentChannels = get_channels()
        currentChannels.pop(channel)
        else:
            with open("channels.json", "w", encoding="utf8") as f:
                f.write(json.dumps({"channels":currentChannels}, indent=4))
            await ctx.send("**Channel removed successfully**")
    except Exception as e:
        await ctx.send(e)

@bot.event
async def on_ready():
    print("Ich habe mich eingeloggt. Beep bop.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ZIB 20"))
    bot.loop.create_task(read_news())
 
    
async def read_news():
    while True:
        with open("news.txt", "r", encoding="utf8") as f:
            line = f.readline()
        
        with open("url.txt", "r", encoding="utf8") as f:
            url = f.readline()
            
        await check_news(line, url)
        await asyncio.sleep(600)
        
            
async def check_news(line, url):
    page = requests.get('https://orf.at/')
    tree = html.fromstring(page.content)
    
    news = tree.xpath("//div[@class='ticker-ressort inland']//*[@class='ticker-story-headline']//a/text()")[0]
    
    link = tree.xpath("//div[@class='ticker-ressort inland']//div[@class='ticker-story-wrapper']//div[@class='story-story']//a/@href")[0]
    
    if link == url:
        link = tree.xpath("//div[@class='ticker-ressort inland']//*[@class='ticker-story-wrapper']//a/@href")[0]
        
    news = news.strip()

    if line != news and url != link:
        for channel in get_channels():
            try:
                await bot.get_channel(int(channel)).send(link)
            except Exception as e:
                await bot.get_channel(int(channel)).send(f"**{e}**")
                
        await overwrite_news(news, link)
        
    elif line == news:
        pass
        
        
async def overwrite_news(news, link):
    with open("news.txt", "w", encoding="utf8") as f:
        f.write(news)
        
    with open("url.txt", "w", encoding="utf8") as f:
        f.write(link)

        
@bot.command()
async def info(ctx):
    await ctx.send("Großes Dankeschön an **Millor#0001**")
    
    
@bot.command()
async def help(ctx):    
    await ctx.send("`~addChannel` to add Channel for ORF News")
    

bot.run(TOKEN)
