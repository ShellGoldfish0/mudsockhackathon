#imports
import discord
import json
from discord.ext import commands, tasks
import random
from os import getenv
from dotenv import load_dotenv
from discord.utils import get
import asyncio
#end of imports

#opens a json file with students discord names and hashes as well as the bio they input in registration
with open('StudentList.json') as StudentBio:
    bioDict = json.load(StudentBio)

with open('classDict.json') as cl:
    classDict = json.load(cl)
with open('classDict.json', "r") as clist:
    namesList = json.load(clist)
with open('links.json') as linkList:
    linkThingy = json.load(linkList)
intrestList = ["valorant","football","basketball","video games","lacrosse","chess","call of duty","boxing","paintball","games","english","welding","agriculture","coding","hacking","kickboxing","discord","soccer","math","science","construction","cars","fortnite","driving","cooking"]


#token and prefix setup.
TOKEN = "haha funny"
bot = commands.Bot(command_prefix="=")
intrestCounter = {}
def get_key(val):
    for key, value in namesList.items():
        if val == value:
            return key
def find_key(val):
    for key, value in intrestCounter.items():
        if val == value:
            return key

#1st part of setup. Creates the teacher role, which will be used for access to certain commands.
@bot.command(help="1st Part of setup", brief="Sets up roles for bot to use.")
@commands.has_role("Owner")
async def setup1(ctx, name):
    if name == "Teacher":     #checks to make sure the input would make the roles uniform
        guild = ctx.guild
        await guild.create_role(name = name)
        await ctx.send(f'Role has been created')
    else:
        await ctx.send("Make sure your message includes Teacher as the only argument.")
#2nd part of setup. Creates the student role, which will aslo be used during certain commands.
@bot.command(help="2nd part of setup", brief="Finishes Bot role setup")
@commands.has_role("Owner")
async def setup2(ctx, name):
    if name == "Student":    #checks to make sure the input would make the roles uniform
        guild = ctx.guild
        await guild.create_role(name = name)
        await ctx.send(f'Role has been created')
    else:
        await ctx.send("Make sure your message includes Student as the only argument.")
#registration. Due to time, this would be put in a database but due to time constraints im using a json file. This will store student bios, and user hashes.
@bot.command(help="Registers you into the system!", brief="Stores the data you input.")
async def register(ctx):
    try:
        #function used for asking follow up questions.
        def check(m: discord.Message):  # m = discord.Message.
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        await ctx.send("Please, type out your intrests for your teacher to see. They will see this, so do not say anything innapropriate or administrative action might occur.")
        msg = await bot.wait_for("message", check=check, timeout=60)
        discordFullTag = "@" + ctx.author.name + "#" + ctx.author.discriminator
        bio = msg.content
        with open("StudentList.json", "w") as Save:
            bioDict[discordFullTag] = bio
            json.dump(bioDict, Save)
            await ctx.channel.send("You have now been added to our database!")
        await ctx.send("Make sure to use =profile to check out your profile!")
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")
#This command takes The name and formats it into a clean embed, and has their bio as well as a fun little description that is randomly generated.
@bot.command(help="Views your profile!", brief="Checks out the bio you created with =register")
async def profile(ctx):
    def check(m: discord.Message):  # m = discord.Message.
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
    findUser = "@"+ str(ctx.author)
    userFound = findUser in bioDict
    if userFound == True:
        complimentList = ["The smartest", "My Precious", "The Prettiest", "My Favorite", "The Best student", "The Winner", "Clearly The Favorite Student", "The Athlete", "The State Champ", "Sapp's Favorite"]
        compliment  = random.choice(complimentList)
        try:
            await ctx.send("Enter your name please. This is just to make your profile display properly.")
            msg = await bot.wait_for("message", check=check, timeout=60)
            nameHeader = msg.content
            embed = discord.Embed(title = nameHeader, description = compliment, color = 0x0220CC)
            embed.add_field(name = "Bio", value = bioDict[findUser], inline=False)
            await ctx.send(embed = embed)
        except asyncio.TimeoutError:
            await ctx.send("Sorry, you didn't reply in time!")
    else:
        await ctx.send("You are not registered. Use =register to make your profile!")

#this commands put you into classDict.json, and allows future use of commands like analyze and view class.
@bot.command(help="Allows you to join the class roster", brief= "Allows your teacher to view your profile.")
async def joinclass(ctx):
    #function used for asking follow up questions.
    def check(m: discord.Message):  # m = discord.Message.
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
    try :

        discordHash = "@" + str(ctx.author)
        await ctx.send("Enter your full name please.")
        name = await bot.wait_for("message", check=check, timeout=60)
        fullName = name.content
        with open('classDict.json', "r") as tester:
            nameCheck = json.load(tester)
        nameInDict = fullName in nameCheck
        if nameInDict == True:
            await ctx.send(f"Sorry, you are already in the list : )")
        else:
            with open("classDict.json", "w") as Save:
                classDict[fullName] = discordHash
                json.dump(classDict, Save)
                await ctx.send("You've been added to the class!")
                return classDict
    except asyncio.TimeoutError:
        await ctx.send("you took to long, try again.")

#Allows you to visulaize the class in a cleaner format.
@bot.command(help="command for teacher to view whole class.", brief="Allows the class view ina  pleasent format.")
@commands.has_role("Teacher")
async def viewclass(ctx):
    with open('classDict.json', "r") as clist:
        namesList = json.load(clist)
    embed = discord.Embed(title = "List of students", description = "", color = 0x0220CC)
    for name in namesList:
        keyThing = namesList[name]
        nameFinder = get_key(keyThing)
        embed.add_field(name = nameFinder, value = bioDict[keyThing], inline=False)

    await ctx.send(embed = embed)

#does the same as class but on the backend, and then gives summary statistics and suggestions of current news ont those items, using a custom algorithm for searching through bios.
@bot.command(help="Allows the analysis of student bios, and outputs some things that might interest them next class.", brief="Analyzes and outputs some suggestions to talk about.")
@commands.has_role("Teacher")
async def analyze(ctx):
    with open('classDict.json', "r") as clist:
        namesList = json.load(clist)
    with open('StudentList.json') as StudentBios:
        bioDict = json.load(StudentBios)
    intrestCounter = {}
    checker = 0
    def find_key(val):
        for key, value in intrestCounter.items():
            if val == value:
                return key
    for words in intrestList:
        subWords = intrestList[checker]
        intrestCounter[subWords] = 0
        checker+=1
    checker = 0
    for name in namesList:
        keyThing = namesList[name]
        bioThing = bioDict[keyThing]
        nameFinder = get_key(keyThing)
        for words in intrestList:
            subWords = intrestList[checker]
            checkWord = subWords in bioDict[keyThing]
            if checkWord == True:
                intrestCounter[subWords] += 1
                checker +=1
            else:
                checker+=1
            if checker >= len(intrestList):
                checker = 0
    highest = 0
    secondHighest = 0
    thirdHighest = 0
    for words in intrestList:
        for x in intrestCounter:
            subWords = intrestList[checker]
            if intrestCounter[subWords] != 0:
                temp = intrestCounter[subWords]
                if highest == 0:
                    highest = temp
                    checker+=1
                elif temp >= highest:
                    highest = secondHighest
                    highest = temp
                    checker+=1
                elif temp < highest and temp > secondHighest:
                    secondHighest = temp
                    checker+=1
                elif temp < secondHighest and temp > thirdHighest:
                    thirdHighest = temp
                    checker+=1
                else:
                    checker+=1
            else:
                checker+=1
        if checker >= len(intrestCounter):
            checker = 0
    popList = []
    for words in intrestCounter:
        subWords = intrestList[checker]
        if intrestCounter[subWords] == 0:
            popList.append(subWords)
            checker+=1
        else:
            checker+=1
    if checker >= len(intrestCounter):
        checker = 0
    for x in popList:
        intrestCounter.pop(x)
    firstKey = find_key(highest)
    secondKey = find_key(secondHighest)
    thirdKey = find_key(thirdHighest)
    with open('links.json') as linkList:
        linkThingy = json.load(linkList)
    embed = discord.Embed(title = "Summary Statistics", description = "What we found", color = 0x0220CC)
    if highest is not None and highest != 0:
        firstStats = highest/len(namesList)
        firstStats = format(firstStats, ".2f")
        firstStats = float(firstStats) *100
        embed.add_field(name = firstKey, value = f"This is your most popular interest, with a %{firstStats} interest out of your class. We recommend you use {linkThingy[firstKey]} to better interact with your students.", inline=False)
        if secondHighest is not None and secondHighest != 0:
            secondStats = secondHighest/len(namesList)
            secondStats = format(secondStats, ".2f")
            secondStats = float(secondStats) *100
            embed.add_field(name = secondKey, value = f"This is your second most popular interest, with a %{secondStats} interest out of your class. We recommend you use {linkThingy[secondKey]} to better interact with your students.", inline=False)
            if thirdHighest is not None and thirdHighest != 0:
                thirdStats = thirdHighest/len(namesList)
                thirdStats = format(thirdStats, ".2f")
                thirdStats = float(thirdStats) *100
                embed.add_field(name = thirdKey, value = f"This is your third most popular interest, with a %{thirdStats} interest out of your class. We recommend you use {linkThingy[thirdKey]} to better interact with your students.", inline=False)
            else:
                print("no third")
        else:
            print("no second")
    else:
        embed.add_field(name = "Nothing Found!", value = "We couldnt find any interests in your students bios. Have them add theirs using =addintrests")
    await ctx.send(embed = embed)

#allows people to input their intrests if they do not appear in analyze. best when used with viewclass.
@bot.command(help="allows input of more intrests for scanning.", brief="Puts the information into the search database")
async def interests(ctx, arg):
    def check(m: discord.Message):  # m = discord.Message.
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
    intrestList.append(arg)
    await ctx.send("Now, send a link that best associates with your interests.")
    msg = await bot.wait_for("message", check=check, timeout=60)
    link = msg.content
    with open("links.json", "w") as Save:
        linkThingy[arg] = link
        json.dump(linkThingy, Save)
    await ctx.send("Your interest has been recorded. Thank you!")
#sets the status
@bot.event
async def on_ready():
    await changeStatus()
    print("Bot is ready!")
async def changeStatus():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"Currently anlyzing student interests!")
    )
#brings the bot online
bot.run(TOKEN)
