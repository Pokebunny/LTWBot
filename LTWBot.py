# file: LTWBot.py
# author: Nick Taber (Pokebunny)
# date: 5/6/21

# A Discord bot for use in the Line Tower Wars official Discord server.

# CURRENT FEATURES
#   Leaderboard printing from file upload
#   Tower and creep data printing from google spreadsheet
#   Tower and creep trivia

# PLANNED FEATURES

import random
from datetime import datetime
from time import sleep

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("LTWBOT_TOKEN")

bot = commands.Bot(command_prefix='!')

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Open LTW spreadsheet
creep_sheet = client.open("LTW 5.x - Theorycrafting").worksheet("Creep Data")
tower_sheet = client.open("LTW 5.x - Theorycrafting").worksheet("Tower Data")
disc_sheet = client.open("LTW 5.x - Theorycrafting").worksheet("Disc Data")

# Extract and store creep data
creep_data_version = "5.8a"
creep_data = creep_sheet.get_all_records()
for i in reversed(range(len(creep_data))):
    if creep_data[i]["CREEP"] == "":
        del creep_data[i]

# Extract and store tower data
tower_data_version = "5.8a"
tower_data = tower_sheet.get_all_records()
for i in reversed(range(len(tower_data))):
    if tower_data[i]["TOWER"] == "":
        del tower_data[i]

# Extract and store disc data
disc_data_version = "5.8a"
disc_data = disc_sheet.get_all_records()
for i in reversed(range(len(disc_data))):
    if disc_data[i]["DISC"] == "":
        del disc_data[i]

trivia_active = False
current_answer = ""
session_trivia_stats = {}

trivia_margin_of_error = 0.01


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(ctx):
    if ctx.author.name == bot.user:
        return

    if len(ctx.attachments) > 0 and ctx.channel.name == "current-season":
        if ctx.attachments[0].filename == "leaderboard_dump.txt":
            file_name = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " LTW Leaderboard pre-parse.txt"
            open(file_name, "wb").write(requests.get(ctx.attachments[0].url).content)
            lb = open(parse_leaderboard(file_name), encoding="latin-1")
            response = lb.readlines()
            response1 = ""
            response2 = "`"
            for line in response[:51]:
                response1 += line

            response1 += "`"

            for line in response[51:]:
                response2 += line

            messages = await ctx.channel.history(limit=3).flatten()
            await messages[1].delete()
            await messages[2].delete()
            print(ctx.author.name)
            await ctx.channel.send(response1)
            await ctx.channel.send(response2)
            await ctx.delete()

    if trivia_active:
        global current_answer
        if type(current_answer) is float or type(current_answer) is int and ctx.channel.name == "ltw-bot-channel":
            try:
                if current_answer - (current_answer * trivia_margin_of_error) <= float(ctx.content) <= \
                        current_answer + (current_answer * trivia_margin_of_error):
                    await correct_answer(ctx)
            except ValueError:
                pass
        elif str(ctx.content).lower() == str(current_answer).lower() and ctx.channel.name == "ltw-bot-channel":
            await correct_answer(ctx)

    await bot.process_commands(ctx)


# @bot.command(name="leaderboard", help="Prints the latest leaderboard uploaded to the bot")
# async def leaderboard(ctx):
#     lb = open("LTW Leaderboard.txt", encoding="latin-1").readlines()
#     response1 = ""
#     response2 = "`"
#     for line in lb[:51]:
#         response1 += line
#
#     response1 += "`"
#
#     for line in lb[51:]:
#         response2 += line
#
#     await ctx.send(response1)
#     await ctx.send(response2)


def parse_leaderboard(file_name):
    file = open(file_name, encoding="latin-1")
    new_file_name = "LTW Leaderboard.txt"
    new_file = open(new_file_name, "w+", encoding="latin-1")
    leaderboard = file.readlines()
    new_file.write("`")
    for line in leaderboard:
        if line[0] == "*":
            words = line.split()
            username = words[1]
            str_length = 19 - len(words[0])
            line = line.replace("*", "")

            if str_length+1 > len(username) > 2:
                num_spaces = str_length - len(username)
                new_username = username
                while num_spaces > 0:
                    new_username = new_username + ' '
                    num_spaces = num_spaces - 1
                line = line.replace(username, new_username)
            new_file.write(line)
    new_file.write("`")
    return new_file_name


@bot.command(name="tower", help="Type !tower <towername> with no spaces in the tower name to fetch information about "
                                "a tower. Also can match partial tower names.")
async def get_tower(ctx, tower_name):
    response = ""
    if tower_name == "list":
        for t in tower_data:
            response += t["TOWER"] + ", "
    else:
        response = get_tower_data(tower_name)

    if response == "":
        response = "Tower not found. You may need to type the tower name with no spaces, or in quotes."
    if len(response) > 2000:
        response = "Too many towers found, try a more specific term."

    await ctx.send(response)


@bot.command(name="creep", help="Type !creep <creepname> with no spaces in the tower name to fetch information about "
                                "a creep. Also can match partial creep names.")
async def get_creep(ctx, creep_name):
    response = ""
    if creep_name == "list":
        for c in creep_data:
            response += c["CREEP"] + ", "
    else:
        response = get_creep_data(creep_name)

    if response == "":
        response = "Creep not found. You may need to type the creep name with no spaces, or in quotes."
    if len(response) > 2000:
        response = "Too many creeps found, try a more specific term."

    await ctx.send(response)


@bot.command(name="disc", help="Type !disc <element> with no spaces in the tower name to fetch information about "
                                "a disc.")
async def get_disc(ctx, disc_name):
    response = ""
    if disc_name == "list":
        for d in disc_data:
            response += d["DISC"] + ", "
    else:
        response = get_disc_data(disc_name)

    if response == "":
        response = "Disc not found. You may need to type the disc name with no spaces, or in quotes."
    if len(response) > 2000:
        response = "Too many discs found, try a more specific term."

    await ctx.send(response)


def tower_to_string(t):
    response = "**" + t.name + "** *(Version " + tower_data_version + "*)\nElement: " + t.element \
                + "\nBuild/upgrade cost: " + str(t.cost) + " (total value: " + str(t.total_cost) \
                + ")\nDamage: " + str(t.min_damage) + "-" + str(t.max_damage) + "\nHit speed: " \
                + t.hit_speed + "\nRange: " + str(t.range_) + "\nSplash: " + str(t.splash) \
                + "\nTargets: " + t.targets + "\nDamage Type: " + t.damage_type \
                + "\nAbility: " + t.ability_text + "\n\n"
    return response


def get_tower_data(tower_name):
    tower_string = ""
    for tower in tower_data:
        if tower_name.lower().replace(" ", "") == tower["TOWER"].lower().replace(" ", ""):
            tower_string = "**" + tower["TOWER"] + "** *(Version " + tower_data_version + "*)\nElement: " + \
                           tower["Element"] + "\nBuild/upgrade cost: " + str(tower["Gold Cost"]) + " (total value: " + \
                           str(tower["Total Cost"]) + ")\nDamage: " + str(tower["Minimum Damage"]) + "-" + \
                           str(tower["Maximum Damage"]) + "\nAttack speed: " + str(tower["Attack Speed"]) + "s\nRange: " + \
                           str(tower["Attack Range"]) + "\nSplash: " + str(tower["Splash"]) + \
                           "\nTargets: " + tower["Targets"] + "\nDamage Type: " + tower["Damage Type"] + \
                           "\nAbility: " + tower["Ability"] + "\n\n"
        elif tower_name.lower().replace(" ", "") in tower["TOWER"].lower().replace(" ", ""):
            tower_string += "**" + tower["TOWER"] + "** *(Version " + tower_data_version + "*)\nElement: " + \
                           tower["Element"] + "\nBuild/upgrade cost: " + str(tower["Gold Cost"]) + " (total value: " + \
                           str(tower["Total Cost"]) + ")\nDamage: " + str(tower["Minimum Damage"]) + "-" + \
                           str(tower["Maximum Damage"]) + "\nAttack speed: " + str(tower["Attack Speed"]) + "s\nRange: " + \
                           str(tower["Attack Range"]) + "\nSplash: " + str(tower["Splash"]) + \
                           "\nTargets: " + tower["Targets"] + "\nDamage Type: " + tower["Damage Type"] + \
                           "\nAbility: " + tower["Ability"] + "\n\n"

    return tower_string


def get_creep_data(creep_name):
    creep_string = ""
    for creep in creep_data:
        if creep_name.lower().replace(" ", "") == creep["CREEP"].lower().replace(" ", ""):
            creep_string = "**" + creep["CREEP"] + "** *(Version " + creep_data_version + ")*\nTier: " + \
                           str(creep["TIER"]) + "\nCost: " + str(creep["GOLD COST"]) + "\nIncome: " + \
                           str(creep["INCOME"]) + "\nBounty: " + str(creep["BOUNTY"]) + "\nHealth: " + \
                           str(creep["HP"]) + "\nArmor: " + str(creep["ARMOR"]) + "\nArmor Type: " + \
                           creep["ARMOR TYPE"] + "\nMove speed: " + str(creep["MOVE SPEED"]) + "\nTraits: " + \
                           creep["TRAITS"]
            break
        elif creep_name.lower().replace(" ", "") in creep["CREEP"].lower().replace(" ", ""):
            creep_string += "**" + creep["CREEP"] + "** *(Version " + creep_data_version + ")*\nTier: " + \
                            str(creep["TIER"]) + "\nCost: " + str(creep["GOLD COST"]) + "\nIncome: " + \
                            str(creep["INCOME"]) + "\nBounty: " + str(creep["BOUNTY"]) + "\nHealth: " + \
                            str(creep["HP"]) + "\nArmor: " + str(creep["ARMOR"]) + "\nArmor Type: " + \
                            creep["ARMOR TYPE"] + "\nMove speed: " + str(creep["MOVE SPEED"]) + "\nTraits: " + \
                            creep["TRAITS"] + "\n\n"

    return creep_string


def get_disc_data(disc_name):
    disc_string = ""
    for disc in disc_data:
        if disc_name.lower().replace(" ", "") in disc["DISC"].lower().replace(" ", ""):\
            disc_string += "**" + disc["DISC"] + "** *(Version " + disc_data_version + ")*\n" + disc["EFFECT"] + "\n\n"

    return disc_string


@bot.command(name="trivia", help="Starts the bot running Line Tower Wars trivia.")
async def trivia(ctx, param):
    global trivia_active
    if param == "start":
        trivia_active = True
        await ask_trivia_question(ctx)

    if param == "stop":
        global current_answer
        current_answer = ""
        await ctx.channel.send("Trivia stopped, saving statistics...")
        global session_trivia_stats
        await ctx.channel.send("Session statistics:")
        await ctx.channel.send(session_trivia_stats)
        file = open("trivia_stats.txt", "r", encoding="latin-1")
        stats = file.readlines()
        total_trivia_stats = {}
        for line in stats:
            user = line.split()[0]
            correct_answer_count = int(line.split()[1])
            total_trivia_stats[user] = correct_answer_count
            if user in session_trivia_stats:
                total_trivia_stats[user] += session_trivia_stats[user]
                del session_trivia_stats[user]
        for user, score in session_trivia_stats.items():
            total_trivia_stats[user] = score
        file = open("trivia_stats.txt", "w", encoding="latin-1")
        file.truncate(0)
        for user, score in total_trivia_stats.items():
            file.write(user + " " + str(score) + "\n")
        await ctx.channel.send("All time statistics:")
        await ctx.channel.send(total_trivia_stats)

        session_trivia_stats = {}
        trivia_active = False


async def ask_trivia_question(ctx):
    (question, answer) = create_trivia_question()
    await ctx.channel.send(question)
    global current_answer
    current_answer = answer


def create_trivia_question():
    topic = random.choice(["tower", "creep", "tower"])
    question = ""
    answer = ""
    if topic == "tower":
        tower = random.choice(tower_data)
        attribute_list = list(tower.keys())
        print(attribute_list)
        attribute_list.remove("DPS (Single Target)")
        attribute_list.remove("DPS/Gold Cost Ratio")
        attribute_list.remove("Minimum Damage")
        attribute_list.remove("Maximum Damage")
        attribute_list.remove("Targets")
        if tower["Ability"] == "N/A":
            attribute_list.remove("Ability")
            attribute_list.remove("TOWER")
        attribute = random.choice(attribute_list)
        if attribute == "TOWER" or attribute == "Ability":
            question = "What tower has this ability?\n" + tower["Ability"]
            answer = tower["TOWER"]
        else:
            question = "What is the " + attribute + " of " + tower["TOWER"] + "?"
            answer = tower[attribute]

    elif topic == "creep":
        creep = random.choice(creep_data)
        attribute_list = list(creep.keys())
        attribute_list.remove("INC. RATIO")
        attribute_list.remove("HP")
        attribute_list.remove("BOU. RATIO")
        attribute_list.remove("EHP")
        attribute_list.remove("HP RATIO")
        attribute_list.remove("EHP RATIO")
        attribute_list.remove("HP REG")
        attribute_list.remove("FLYING")
        attribute_list.remove("ATTACKER")
        attribute_list.remove("STOCK S.")
        attribute_list.remove("(IN GAME TIME)")
        attribute_list.remove("DESCRIPTION")
        attribute = random.choice(attribute_list)
        if attribute == "CREEP" or attribute == "TRAITS":
            question = "What creep has these traits?\n" + creep["TRAITS"]
            answer = creep["CREEP"]
        else:
            question = "What is the " + attribute + " of " + creep["CREEP"] + "?"
            answer = creep[attribute]

    return question, answer


async def correct_answer(ctx):
    global current_answer
    previous_answer = current_answer
    current_answer = ""
    await ctx.channel.send(ctx.author.name + " was correct! The answer was " + str(previous_answer))
    if ctx.author.name in list(session_trivia_stats.keys()):
        session_trivia_stats[ctx.author.name] += 1
    else:
        session_trivia_stats[ctx.author.name] = 1

    sleep(5)
    await ask_trivia_question(ctx)


bot.run(TOKEN)
