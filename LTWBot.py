# file: LTWBot.py
# author: Nick Taber (Pokebunny)
# date: 4/8/21

# A Discord bot for use im the Line Tower Wars official Discord server.

# CURRENT FEATURES
#   Leaderboard printing from local file
#   Tower data printing

# PLANNED FEATURES
#   Complete tower data entry
#   Creep data printing
#   Migrate data source to Google Sheets and integrate
#   Allow users to provide updated leaderboard data

from datetime import datetime
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
creep_sheet = client.open("LTW 5.1 - Theorycrafting").worksheet("Creep Data")
tower_sheet = client.open("LTW 5.1 - Theorycrafting").worksheet("Tower Data")

# Extract and store creep data
creep_data_version = "5.3b"
creep_data = creep_sheet.get_all_records()

# Extract and store tower data
tower_data_version = "5.3b"
tower_data = tower_sheet.get_all_records()


@bot.event
async def on_message(ctx):
    if ctx.author.name == bot.user:
        return

    if len(ctx.attachments) > 0:
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

            await ctx.channel.send(response1)
            await ctx.channel.send(response2)

    await bot.process_commands(ctx)


@bot.command(name="leaderboard", help="Prints the latest leaderboard uploaded to the bot")
async def leaderboard(ctx):
    lb = open("LTW Leaderboard.txt", encoding="latin-1").readlines()
    response1 = ""
    response2 = "`"
    for line in lb[:51]:
        response1 += line

    response1 += "`"

    for line in lb[51:]:
        response2 += line

    await ctx.send(response1)
    await ctx.send(response2)


@bot.command(name="tower")
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


@bot.command(name="creep")
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


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


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
                           str(tower["Total Cost"]) + ")\nDamage: " + str(tower["DMG Min"]) + "-" + \
                           str(tower["DMG Max"]) + "\nAttack speed: " + str(tower["Atk. Speed"]) + "s\nRange: " + \
                           str(tower["Atk. Range"]) + "\nSplash: " + str(tower["Splash"]) + \
                           "\nTargets: " + tower["Targets"] + "\nDamage Type: " + tower["Damage Type"] + \
                           "\nAbility: " + tower["Ability"] + "\n\n"
        elif tower_name.lower().replace(" ", "") in tower["TOWER"].lower().replace(" ", ""):
            tower_string += "**" + tower["TOWER"] + "** *(Version " + tower_data_version + "*)\nElement: " + \
                           tower["Element"] + "\nBuild/upgrade cost: " + str(tower["Gold Cost"]) + " (total value: " + \
                           str(tower["Total Cost"]) + ")\nDamage: " + str(tower["DMG Min"]) + "-" + \
                           str(tower["DMG Max"]) + "\nAttack speed: " + str(tower["Atk. Speed"]) + "s\nRange: " + \
                           str(tower["Atk. Range"]) + "\nSplash: " + str(tower["Splash"]) + \
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


bot.run(TOKEN)
