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

# Extract and store creep data
creep_data_version = "5.2c"
creep_data = creep_sheet.get_all_records()


class Tower:
    def __init__(self, name, element, cost, total_cost, min_damage, max_damage, hit_speed, range_, splash, targets,
                 damage_type, ability_text):
        self.name = name
        self.element = element
        self.cost = cost
        self.total_cost = total_cost
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.hit_speed = hit_speed
        self.range_ = range_
        self.splash = splash
        self.targets = targets
        self.damage_type = damage_type
        self.ability_text = ability_text


tower_data_version = "5.2c"
towers = [
    # basic ranged towers
    # name, element, cost, total cost, min damage, max damage, hit speed, range, splash, targets, damage type, ability
    Tower("Archer", "Basic", 10, 10, 1, 1, "0.66s", 400, 0, "Ground, Air", "Piercing", "N/A"),
    Tower("Gunner", "Basic", 30, 40, 3, 3, "0.63s", 500, 0, "Ground, Air", "Piercing", "N/A"),
    Tower("Watch Tower", "Basic", 150, 190, 8, 9, "0.5s", 700, 0, "Ground, Air", "Piercing", "N/A"),
    Tower("Guard Tower", "Basic", 1000, 1190, 37, 38, "0.5s", 700, 0, "Ground, Air", "Piercing", "N/A"),
    Tower("Ward Tower", "Basic", 5000, 6190, 140, 141, "0.5s", 800, 0, "Ground, Air", "Piercing", "N/A"),
    Tower("Ultimate Ward Tower", "Basic", 25000, 31190, 527, 528, "0.5s", 900, 0, "Ground, Air", "Piercing", "N/A"),
    Tower("Cannon Tower", "Basic", 150, 190, 14, 16, "2.0s", 500, 150, "Ground", "Siege", "N/A"),
    Tower("Bombard Tower", "Basic", 1000, 1190, 70, 74, "2.0s", 550, 200, "Ground", "Siege", "N/A"),
    Tower("Artillery Tower", "Basic", 5000, 6190, 279, 283, "2.0s", 600, 250, "Ground", "Siege", "N/A"),
    Tower("Ultimate Artillery Tower", "Basic", 25000, 31190, 1050, 1058, "2.0s", 650, 300, "Ground", "Siege", "N/A"),

    # basic melee towers
    Tower("Cutter", "Basic", 10, 10, 1, 1, "0.33s", 150, 0, "Ground", "Normal", "N/A"),
    Tower("Grinder", "Basic", 30, 40, 3, 3, "0.33s", 150, 0, "Ground", "Normal", "N/A"),
    Tower("Carver", "Basic", 150, 190, 13, 15, "0.33s", 150, 0, "Ground", "Normal", "N/A"),
    Tower("Executioner", "Basic", 1000, 1190, 69, 75, "0.33s", 150, 0, "Ground, Air", "Normal", "N/A"),
    Tower("Mauler", "Basic", 5000, 6190, 291, 299, "0.33s", 200, 0, "Ground, Air", "Normal", "N/A"),
    Tower("Ultimate Mauler", "Basic", 25000, 31190, 1180, 1191, "0.33s", 200, 0, "Ground, Air", "Normal", "N/A"),
    Tower("Crusher", "Basic", 150, 190, 25, 28, "5.0s", 150, 275, "Ground, Air", "Normal", "N/A"),
    Tower("Wrecker", "Basic", 1000, 1190, 112, 117, "5.0s", 150, 350, "Ground, Air", "Normal", "N/A"),
    Tower("Mangler", "Basic", 5000, 6190, 494, 501, "5.0s", 150, 425, "Ground, Air", "Normal", "N/A"),
    Tower("Ultimate Mangler", "Basic", 25000, 31190, 1996, 2004, "5.0s", 150, 500, "Ground, Air", "Normal", "N/A"),

    # elemental towers
    Tower("Elemental Core", "Basic", 200, 200, 6, 7, "1.0s", 600, 0, "Ground, Air", "Magic", "N/A"),

    # fire towers
    Tower("Fire Pit", "Fire", 0, 200, 21, 23, "2.5s", 400, 150, "Ground, Air", "Normal",
          "Ignite (1) - Ignites a random creep every 2.1 second in a 400 radius, dealing 5 Spell Damage per second "
          "over 5 seconds."),
    Tower("Magma Well", "Fire", 800, 1000, 70, 75, "2.5s", 400, 200, "Ground, Air", "Normal",
          "Ignite (2) - Ignites a random creep every 2.1 second in a 400 radius, dealing 13 Spell Damage per second "
          "over 5 seconds."),
    Tower("Meteor Attractor", "Fire 1 - Meteor Attractor", 4000, 5000, 201, 205, "2.5s", 800, 300, "Ground", "Siege",
          "Overwhelming Impact (1) - Attracts meteors towards the ground, causing them to light the ground on fire for "
          "2 seconds and burn enemy units for 23 Spell Damage per second."),
    Tower("Armageddon", "Fire 1 - Meteor Attractor", 10000, 15000, 432, 436, "2.5s", 975, 400, "Ground", "Siege",
          "Overwhelming Impact (2) - Attracts meteors towards the ground, causing them to light the ground on fire for "
          "2 seconds and burn enemy units for 87 Spell Damage per second."),
    Tower("Ultimate Moonbeam Projector", "Fire 1 - Meteor Attractor\n*Requires Void 1 - Riftweaver*", 30000, 45000,
          1089, 1092, "2.5s", 1150, 500, "Ground", "Siege",
          "Void Flare - Regenerates 5 mana per second. Projects a Void Flare for 3 seconds when at 100% mana: dealing "
          "816 Spell Damage to all creeps within a 500 radius every second. Creeps within the Void Flare also takes "
          "40% additional Spell Damage. Void Flare resets mana back to 0."),
    Tower("Living Flame", "Fire 2 - Living Flame", 4000, 5000, 79, 83, "0.5s", 400, 50, "Ground, Air", "Chaos",
          "Rising Heat (1) - Each attack lowers attack speed by 0.02s. Reaching below 0.2s attack speed will reset "
          "attack speed back to 0.5s."),
    Tower("Hellfire", "Fire 2 - Living Flame", 1000, 15000, 149, 153, "0.4s", 400, 50, "Ground, Air", "Chaos",
          "Rising Heat (2) - Each attack lowers attack speed by 0.0033s. Reaching below 0.1s attack speed will reset "
          "attack speed back to 0.4s."),
    Tower("Ultimate Firelord", "Fire 2 - Living Flame\n*Requires Lightning 1 - Lightning Beacon*", 30000, 45000, 368,
          372, "0.4s", 500, 150, "Ground, Air", "Chaos",
          "Volcanic Eruption - 40% chance to explode a random damaged creep; dealing 500% additional damage of the "
          "damage dealt as Spell Damage and permanently reducing its current armor by 25% down to 0. Attacking a "
          "target with less than 40% health increases attack speed by 35%."),

    # ice towers
    Tower("Frozen Obelisk", "Ice", 0, 200, 11, 14, "1.5s", 500, 50, "Ground, Air", "Magic",
          "Frost Attack (1) - Each attack chills the target unit; reducing movement speed by 2.5% up to 25%."),
    Tower("Runic Obelisk", "Ice", 800, 1000, 39, 43, "1.5s", 600, 50, "Ground, Air", "Magic",
          "Frost Attack (2) - Each attack chills the target unit; reducing movement speed by 3% up to 30%."),
    Tower("Frozen Watcher", "Ice 1 - Frozen Watcher", 4000, 5000, 104, 108, "1.0s", 600, 75, "Ground, Air", "Magic",
          "Frost Blast (1) - Each attack chills the target unit; reducing movement speed by 4%, up to 40%."),
    Tower("Frozen Core", "Ice 1 - Frozen Watcher", 10000, 15000, 307, 311, "1.0s", 600, 100, "Ground, Air", "Magic",
          "Frost Blast (2) - Each attack chills the target unit: reducing movement speed by 4.5%, up to 45%."),
    Tower("Ultimate Lich", "Ice 1 - Frozen Watcher\n*Requires Unholy 1 - Septic Tank*", 30000, 45000, 581, 585, "1.0s",
          600, 150, "Ground, Air", "Magic",
          "Chilling Death - Each attack chills the target unit; reducing movement speed by 5.5% up to 55%. The bitter "
          "cold of death spreads around the Lich, reducing health regeneration of creeps within a 300 radius by 100%."),
    Tower("Icicle", "Ice 2 - Icicle", 4000, 5000, 97, 99, "1.0s", 600, 0, "Ground, Air", "Piercing",
          "Ice Lance (1) - Attacks pierce and hit all creeps in a line towards the target creep, up to 600 distance "
          "and creeps hit have their armor permanently reduced by 0.2, down to 0."),
    Tower("Tricicle", "Ice 2 - Icicle", 10000, 15000, 250, 252, "1.0s", 700, 0, "Ground, Air", "Piercing",
          "Ice Lance (2) - Attacks pierce and hit all creeps in a line towards the target creep, up to 700 distance "
          "and creeps hit have their armor permanently reduced by 0.25, down to 0."),
    Tower("Ultimate Crystal", "Ice 2 - Icicle\n*Requires Holy 1 - Lightshroom*", 30000, 45000, 823, 828, "1.0s", 800, 0,
          "Ground, Air", "Piercing",
          "Crystallized Light - Attacks pierce and hit all creeps in a line towards the target creep, up to 800 "
          "distance and creeps hit have their armor permanently reduced by 0.4, down to 0. The damage dealt is "
          "increased by 100% for the first target hit and then reduced by 5% for each target hit down to 0% bonus "
          "damage."),

    # lightning towers
    Tower("Shock Particle", "Lightning", 0, 200, 15, 15, "0.5s", 200, 0, "Ground, Air", "Chaos",
          "Overcharge (1) - Attacks deal 1 additional damage for every 10% current health of the target."),
    Tower("Shock Generator", "Lightning", 800, 1000, 60, 60, "0.5s", 200, 0, "Ground, Air", "Chaos",
          "Overcharge (2) - Attacks deal 5 additional damage for every 10% current health of the target"),
    Tower("Lightning Beacon", "Lightning 1 - Lightning Beacon", 4000, 5000, 348, 362, "2.0s", 1000, 0, "Ground, Air",
          "Chaos",
          "Focused Lightning (1) - Each attack on the same target increases base damage by 50%; attacking a new target "
          "resets the bonus damage."),
    Tower("Lightning Generator", "Lightning 1 - Lightning Beacon", 10000, 15000, 810, 824, "2.0s", 1250, 0,
          "Ground, Air", "Chaos",
          "Focused Lightning (2) - Each attack on the same target increases base damage by 75%; attacking a new target "
          "resets the bonus damage."),
    Tower("Ultimate Annihilation Glyph", "Lightning 1 - Lightning Beacon\nRequires Unholy 2 - Decayed Guardian", 30000,
          45000, 1964, 1976, "2.0s", 1500, 0, "Ground, Air", "Chaos",
          "Annihilation - Each attack on the same target increases base damage by 100%; attacking a new target resets "
          "the bonus damage. The damage dealt will chain to 2 additional targets, dealing 25% reduced damage after "
          "each hit."),
    Tower("Voltage", "Lightning 2 - Voltage", 4000, 5000, 130, 130, "0.33s", 200, 0, "Ground, Air", "Chaos",
          "Electrocute (1) - Deals additional damage equal to 1% of the target's current health and the damage dealt "
          "is stored as 1 Static Charge; maximum of 5 charges. On 3 Static Charges a lightning bolt strikes a random "
          "nearby air creep within a 300 radius: dealing Spell Damage equal to the stored damage of the Static Charges."
          " The Static Charges are reset after each lightning bolt."),
    Tower("High Voltage", "Lightning 2 - Voltage", 10000, 15000, 350, 350, "0.33s", 200, 0, "Ground, Air", "Chaos",
          "Electrocute (2) - Deals additional damage equal to 2% of the target's current health and the damage dealt "
          "is stored as 1 Static Charge; maximum of 5 charges. On 3 Static Charges a lightning bolt strikes a random "
          "nearby air creep within a 300 radius: dealing Spell Damage equal to the stored damage of the Static Charges."
          " The Static Charges are reset after each lightning bolt."),
    Tower("Ultimate Orb Keeper", "Lightning 2 - Voltage\n*Requires Holy 2 - Sunray Tower*", 30000, 45000, 560, 560,
          "0.33s", 200, 0, "Ground, Air", "Chaos",
          "Radiance - Attacks shock nearby creeps within a 200 radius, reducing their current health by 0.5%."),

    # holy towers
    Tower("Light Flies", "Holy", 0, 200, 12, 13, "2.0s", 800, 0, "Ground, Air", "Piercing",
          "Bursting Light (1) - Attacks hit 3 additional targets and cause them to take 10% additional Spell Damage "
          "for 3 seconds."),
    Tower("Holy Lantern", "Holy", 800, 1000, 30, 32, "2.0s", 850, 0, "Ground, Air", "Piercing",
          "Bursting Light (2) - Attacks hit 4 additional targets and cause them to take 10% additional Spell Damage "
          "for 3 seconds."),
    Tower("Lightshroom", "Holy 1 - Lightshroom", 4000, 5000, 87, 90, "1.0s", 400, 200, "Air", "Piercing",
          "Rejuvenating Spores (1) - Consumes 1 mana for every flying non-boss creep hit, pushing it back a distance "
          "of 5.75. If no mana was consumed, the pushback effect is cancelled. Regenerates 10 mana every second. "
          "Additionally, 7.5% of damage dealt heals friendly towers within a 300 radius."),
    Tower("Enchanted Lightshroom", "Holy 1 - Lightshroom", 10000, 15000, 384, 389, "1.0s", 400, 250, "Air", "Piercing",
          "Rejuvenating Spores (2) - Consumes 1 mana for every flying non-boss creep hit, pushing it back a distance "
          "of 7.13. If no mana was consumed, the pushback effect is cancelled. Regenerates 10 mana every second. "
          "Additionally, 10% of damage dealt heals friendly towers within a 300 radius."),
    Tower("Ultimate Divine Lightshroom", "Holy 1 - Lightshroom\n*Requires Water 1 - Water Elemental*", 30000, 45000,
          907, 908, "1.0s", 400, 300, "Air", "Piercing",
          "Divine Spores - Consumes 1 mana for every flying non-boss creep hit, pushing it back a distance of 10.7. "
          "If no mana was consumed the pushback effect is cancelled. Regenerates 10 mana every second. "
          "Additionally, 12% of damage dealt heals friendly towers within a 300 radius."),
    Tower("Sunray Tower", "Holy 2 - Sunray Tower", 4000, 5000, 85, 86, "2.0s", 900, 200, "Ground, Air", "Normal",
          "Blinding Light (1) - Attacks hit 6 additional targets and cause them to take 15% additional Spell Damage and"
          " have 10% reduced attack damage for 3 seconds.Increases armor of nearby friendly towers by 2 within a 500 "
          "radius."),
    Tower("Purified Sunray Tower", "Holy 2 - Sunray Tower", 10000, 15000, 215, 216, "2.0s", 1000, 200, "Ground, Air",
          "Normal",
          "Blinding Light (2) - Attacks hit 8 additional targets and cause them to take 15% additional Spell Damage "
          "and have 15% reduced attack damage for 3 seconds.Increases armor of nearby friendly towers by 3 within "
          "a 500 radius."),
    Tower("Ultimate Titan Vault", "Holy 2 - Sunray Tower\n*Requires Fire 1 - Meteor Attractor*", 30000, 45000, 624, 648,
          "2.0s", 1000, 200, "Ground, Air", "Normal",
          "Titan Defense Mechanism - Attacks hit 10 additional targets. Creeps within a 500 radius have their attack "
          "damage reduced by 20%, movement speed slowed by 15%, and take 25% additional Spell Damage. "
          "Increases armor of nearby friendly towers by 5 within a 500 radius."),

    # void towers
    Tower("Voidling", "Void", 0, 200, 44, 47, "3.0s", 400, 0, "Ground, Air", "Chaos",
          "Void Growth (1) - Regenerates 1 mana every second; attacking at 30 mana the Voidling destroys a nearby "
          "Archer or Cutter within a 400 radius and spawns another Voidling at its location. If no Archer or Cutter "
          "is found it searches for a Gunner or Grinder instead. The spawned Voidling is sold at a reduced price "
          "equal to the value of the replaced tower. This effect can only trigger once."),
    Tower("Voidalisk", "Void", 800, 1000, 219, 222, "3.0s", 400, 0, "Ground, Air", "Chaos",
          "Void Growth (2) - Regenerates 1 mana every second: attacking at 30 mana the Voidling transforms a nearby "
          "Voidling within a 400 radius and spawns another Voidling at its location.The spawned Voidalisk is sold at "
          "a reduced price equal to the value of the replaced towers.This effect can only trigger once."),
    Tower("Riftweaver", "Void 1 - Riftweaver", 4000, 5000, 265, 266, "2.0s", 600, 0, "Ground, Air", "Magic",
          "Temporal Rift (1) - Regenerates 10 mana every second. At 100% mana, marks the location of a target "
          "non-spell resistant creep and after a 3 seconds delay the creep will be brought back to the marked "
          "location and take Spell Damage equal to 5% of its maximum health. If the target is immune, a nearby creep "
          "within a 200 radius is targeted instead. This effect can only trigger once every 9 seconds on the same "
          "creep and the effect is cancelled if the creep steals a life."),
    Tower("Rift Lord", "Void 1 - Riftweaver", 10000, 15000, 812, 813, "2.0s", 600, 0, "Ground, Air", "Magic",
          "Temporal Rift (2) - Regenerates 10 mana every second. At 100% mana, marks the location of a target "
          "non-spell resistant creep and after a 3 second delay the creep will be brought back to the marked location "
          "and take Spell Damage equal to 10% of its maximum health. If the target is immune, a nearby creep within a "
          "200 radius is targeted instead. This effect can only trigger once every 7 seconds on the same creep and the "
          "effect is cancelled if the creep steals a life."),
    Tower("Ultimate Devourer", "Void 1 - Riftweaver\n*Requires Arcane 2 - Arcane Pylon*", 30000, 45000, 2248, 2254,
          "2.0s", 800, 0, "Ground, Air", "Magic",
          "Implosion Rift - Attacks infuse target creeps with void energy over 5 seconds. If a target dies with this "
          "effect, it implodes; dealing 25% of its maximum health as Spell Damage to 1 nearby creep within a 200 "
          "radius, also sending the creep back to spawn. This effect is instantly triggered if the Ultimate Devourer "
          "attacks a creep at 100% mana. Regenerates 10 mana per second and the mana is reset on trigger."),
    Tower("Void Lasher", "Void 2 - Void Lasher", 4000, 5000, 84, 86, "0.7s", 400, 125, "Ground, Air", "Chaos",
          "Void Lashing (1) - Attacks increases attack damage equal to 50% of the current %-health of the primary "
          "target."),
    Tower("Void Ravager", "Void 2 - Void Lasher", 10000, 15000, 217, 219, "0.7s", 400, 150, "Ground, Air", "Chaos",
          "Void Lashing (2) - Attacks increases attack damage equal to 50% of the current %-health of the primary "
          "target."),
    Tower("Ultimate Void Terror", "Void 2 - Void Lasher\n*Requires Earth 2 - Noxious Weed*", 30000, 45000, 484, 486,
          "0.7s", 400, 200, "Ground, Air", "Chaos",
          "Unending Rage - Attacks increase attack damage and attack speed equal to the current %-health of the "
          "primary target and heal equal to 50% of the damage dealt. The healing is reduced by a percentage equal to "
          "the current %-health of the primary target. Unending Rage prevents the Ultimate Void Terror from "
          "regenerating health from health regeneration."),

    # unholy towers
    Tower("Plague Well", "Unholy", 0, 200, 12, 14, "1.0s", 600, 0, "Ground, Air", "Chaos",
          "Corruption (1) - Creeps hit get corrupted for 3 seconds; a corrupted creep will explode when killed, "
          "dealing 22 Spell Damage to nearby enemy creeps."),
    Tower("Catacomb", "Unholy", 800, 1000, 34, 16, "1.0s", 650, 0, "Ground, Air", "Chaos",
          "Corruption (2) - Creeps hit get corrupted for 3 seconds; a corrupted creep will explode when killed, "
          "dealing 56 Spell Damage to nearby enemy creeps."),
    Tower("Septic Tank", "Unholy 1 - Septic Tank", 4000, 5000, 115, 119, "0.6s", 700, 0, "Ground, Air", "Chaos",
          "Death Plague (1) - Infects targets hit; increasing their damage taken by 10% from all sources for "
          "3 seconds."),
    Tower("Plague Fanatic", "Unholy 1 - Septic Tank", 10000, 15000, 323, 327, "0.6s", 700, 0, "Ground, Air", "Chaos",
          "Death Plague (2) - Infects targets hit; increasing their damage taken by 15% from all sources for "
          "3 seconds."),
    Tower("Ultimate Gravedigger", "Unholy 1 - Septic Tank\n*Requires Earth 1 - Earth Protector*", 30000, 45000, 1259,
          1261, "0.6s", 750, 0, "Ground, Air", "Chaos",
          "Gravestrike - Infects targets hit; increasing their damage taken by 20% from all sources for 3 seconds. "
          "Creeps killed by the Gravedigger will reanimate as an undead creature with 300% maximum health of the "
          "killed creep. The creature has no traits and gives no bounty. The reanimated creature is sent towards your "
          "current target enemy lane. This effect has a 35 second cooldown."),
    Tower("Decayed Guardian", "Unholy 2 - Decayed Guardian", 4000, 5000, 75, 80, "1.0s", 300, 100, "Ground, Air",
          "Chaos",
          "Unholy Miasma (1) - (Attacks increases splash by 25, up to 400. This effect is reduced by 10 every second, "
          "down to a minimum of 100."),
    Tower("Decayed Horror", "Unholy 2 - Decayed Guardian", 10000, 15000, 220, 225, "1.0s", 300, 150, "Ground, Air",
          "Chaos",
          "Unholy Miasma (2) - Attacks increases splash by 35, up to 500. This effect is reduced by 15 every "
          "second, down to a minimum of 150."),
    Tower("Ultimate Diabolist", "Unholy 2 - Decayed Guardian\n*Requires Arcane 1 - Archmage*", 30000, 45000, 470, 490,
          "1.0s", 350, 350, "Ground, Air", "Chaos",
          "Hellfire - Damage dealt starts low on the primary target and the damage is ramped up to 2.5% for every "
          "creep caught within the splash radius. If a creep hit is below 3% health it's instantly killed."),

    # water towers
    Tower("Splasher", "Water", 0, 200, 5, 7, "0.5s", 500, 50, "Ground, Air", "Normal",
          "Crushing Wave (1) - Every 5th attack against ground creeps unleashes a Crushing Wave, dealing "
          "5 Spell Damage to all ground creeps hit."),
    Tower("Tidecaller", "Water", 800, 1000, 20, 22, "0.5s", 500, 50, "Ground, Air", "Normal",
          "Crushing Wave (2) - Every 5th attack against ground creeps unleashes a Crushing Wave, dealing "
          "15 Spell Damage to all ground creeps hit."),
    Tower("Water Elemental", "Water 1 - Water Elemental", 4000, 5000, 76, 80, "0.5s", 500, 50, "Ground, Air", "Normal",
          "Pressuring Water (1) - Deals up to 50% additional damage based of the distance from the target creep. The "
          "closer the distance from the Water Elemental, the greater the bonus damage. Attacks also permanently "
          "reduces the armor of target creeps by 0.05, down to 0 armor."),
    Tower("Volatile Water Elemental", "Water 1 - Water Elemental", 10000, 15000, 180, 184, "0.5s", 500, 125,
          "Ground, Air", "Normal",
          "Pressuring Water (2) - Deals up to 70% additional damage based of the distance from the target creep. The "
          "closer the distance from the Water Elemental, the greater the bonus damage. Attacks also permanently "
          "reduces the armor of target creeps by 0.07, down to 0 armor."),
    Tower("Ultimate Hurricane Elemental", "Water 1 - Water Elemental\n*Requires Lightning 2 - Voltage*", 30000, 45000,
          507, 513, "0.5s", 500, 125, "Ground, Air", "Normal",
          "Hurricane Storm - Deals up to 100% additional damage based of the distance from the target creep. The "
          "closer the distance from the Hurricane Elemental, the greater the bonus damage. 20% chance to paralyze "
          "flying creeps, dropping them to the ground for 2 seconds: paralyzed creeps can be attacked as though they "
          "were ground creeps. Can only trigger once every 6 seconds on the same creep (12 seconds for Spell Resistant "
          "/ Immune creeps.)"),
    Tower("Tidal Guardian", "Water 2 - Tidal Guardian", 4000, 5000, 441, 443, "2.0s", 600, 0, "Ground, Air", "Normal",
          "Torrent (1) - Creeps within a 200 radius are slowed by 4% every 2 seconds, up to 20%."),
    Tower("Tidal Monstrosity", "Water 2 - Tidal Guardian", 1000, 15000, 1072, 1074, "2.0s", 600, 0, "Ground, Air",
          "Normal",
          "Torrent (2) - Creeps within a 225 radius are slowed by 5% every 2 seconds, up to 25%."),
    Tower("Ultimate Sludge Monstrosity", "Water 2 - Tidal Guardian\n*Requires Void 2 - Void Lasher*", 30000, 45000,
          2272, 2322, "1.5s", 600, 0, "Ground, Air", "Normal",
          "Crippling Decay - Creeps within a 300 radius takes 10% additional damage from attacks and are slowed by 8% "
          "every 1.5 seconds, up to 40%. Creeps attacked by the Sludge Monstrosity have their attack speed reduced by "
          "25% for 3 seconds."),

    # earth towers
    Tower("Rockfall", "Earth", 0, 200, 16, 20, "2.5s", 300, 250, "Ground", "Siege",
          "Shatter Armor (1) - Attacks reduce the armor of creeps hit by 1 for 5 seconds."),
    Tower("Avalanche", "Earth", 800, 1000, 75, 87, "2.5s", 300, 250, "Ground", "Siege",
          "Shatter Armor (2) - Attacks reduce the armor of creeps hit by 2 for 5 seconds."),
    Tower("Earth Protector", "Earth 1 - Earth Protector", 4000, 5000, 218, 236, "2.5s", 400, 350, "Ground", "Siege",
          "Devastating Attack (1) - 35% chance to permanently reduce the armor of creeps hit by 0.5, down to 0 armor."),
    Tower("Ancient Earth Protector", "Earth 1 - Earth Protector", 10000, 15000, 511, 530, "2.5s", 450, 350, "Ground",
          "Siege",
          "Devastating Attack (2) - 35% chance to permanently reduce the armor of creeps hit by 0.75, down to 0 armor."),
    Tower("Ultimate Ancient Warden", "Earth 1 - Earth Protector\n*Requires Water 2 - Tidal Guardian*", 30000, 45000,
          1475, 1542, "2.5s", 500, 400, "Ground", "Siege",
          "Nature's Guidance - Heals for 2.8% of damage dealt and attacks have a 40% chance to permanently reduce "
          "the armor of creeps hit by 1, down to 0 armor."),
    Tower("Noxious Weed", "Earth 2 - Noxious Weed", 4000, 5000, 131, 141, "0.7s", 650, 0, "Ground, Air", "Piercing",
          "Germinate (1) - When not attacking for over 1 second the damage of the next 3 attacks are increased by 10% "
          "every 0.5 second, up to 50%."),
    Tower("Noxious Thorn", "Earth 2 - Noxious Weed", 10000, 15000, 344, 352, "0.7s", 650, 0, "Ground, Air", "Piercing",
          "Germinate (2) - When not attacking for over 1 second the damage of the next 3 attacks are increased by "
          "15% every 0.5 second, up to 75%."),
    Tower("Ultimate Scorpion", "Earth 2 - Noxious Weed\n*Requires Ice 1 - Frozen Watcher*", 30000, 45000, 905, 932,
          "0.4s", 700, 0, "Ground, Air", "Piercing",
          "Lethal Strike - Attacks have a chance based on the current %-health of the damaged creep to deal 100% "
          "additional damage; lower health equals higher chance. When not attacking for over 1 second the damage of the"
          " next 5 attacks are increased by 15% every 0.5 second, up to 150%."),

    # arcane towers
    Tower("Spellslinger", "Arcane", 0, 200, 4, 4, "0.33s", 1000, 0, "Ground, Air", "Magic",
          "Arcanize (1) - Attacks increase mana by 1. At maximum mana capacity, damage dealt is increased by 100%."),
    Tower("Spellslinger Master", "Arcane", 200, 800, 10, 11, "0.33s", 1000, 0, "Ground, Air", "Magic",
          "Arcanize (2) - Attacks increase mana by 1. At maximum mana capacity, damage dealt is increased by 200%."),
    Tower("Archmage", "Arcane 1 - Archmage", 4000, 5000, 45, 48, "1.0s", 800, 0, "Ground, Air", "Magic",
          "Spellcast (1) - Casts a random spell at 100% mana; Frostbolt: Deals 42 Spell Damage and chills up to 3 "
          "target creeps; reducing their movement speed by 30% for 3 seconds. Firebolt: Firebolts up to 3 target "
          "creeps; dealing 116 Spell Damage and stuns for 0.4 second. Regenerates 33 mana per second and casting "
          "a spell resets mana back to 0%."),
    Tower("Grand Archmage", "Arcane 1 - Archmage", 10000, 15000, 196, 198, "1.0s", 800, 0, "Ground, Air", "Magic",
          "Spellcast (2) - Casts a random spell at 100% mana; Frostblast: Deals 183 Spell Damage and chills up to 3 "
          "target creeps; reducing their movement speed by 40% and attack speed by 25% for 3 seconds. "
          "Pyroblast: Pyroblasts up to 3 target creeps; dealing 590 Spell Damage and stuns for 0.5 second. "
          "Regenerates 33 mana per second and casting a spell resets mana back to 0%."),
    Tower("Ultimate Kirin Tor Wizard", "Arcane 1 - Archmage\n*Requires Ice 2 - Icicle*", 30000, 45000, 812, 815,
          "1.0s", 800, 0, "Ground, Air", "Magic",
          "Kirin Tor Mastery - Casts a random spell at 100% mana; Chains of Ice: Deals 2.315 Spell Damage and chills "
          "up to 5 target creeps; reducing their movement speed by 50% and attack speed by 35% for 3 seconds. "
          "Blizzard: Deals 1590 Spell Damage in a 250 radius and chills the targets hit; reducing movement speed by "
          "30% for 3 seconds. Arcane Blast: Deals 7825 Spell Damage to the current target, also stunning it for "
          "1.0 second. Regenerates 33 mana per second and casting a spell resets mana back to 0%."),
    Tower("Arcane Pylon", "Arcane 2 - Arcane Pylon", 4000, 5000, 39, 41, "0.5s", 900, 0, "Ground, Air", "Magic",
          "Volatile Arcane (1) - Attacks bounce up to 3 times and increase mana by 1 per target hit. For every 1% mana,"
          " base attack speed is lowered by 0.00166, up to 0.166 total. 50% of the damage is dealt as Spell Damage. "
          "Mana decreases by 2.5 every second."),
    Tower("Unstable Arcane Pylon", "Arcane 2 - Arcane Pylon", 10000, 15000, 123, 125, "0.5s", 950, 0, "Ground, Air",
          "Magic",
          "Volatile Arcane (2) - Attacks bounce up to 4 times and increases mana by 1 per target hit. "
          "For every 1% mana, base attack speed is lowered by 0.00166, up to 0.166 total. "
          "50% of the damage is dealt as Spell Damage .Mana decreases by 2.5 every second."),
    Tower("Ultimate Arcane Orb", "Arcane 2 - Arcane Pylon\n*Requires Fire 2 - Living Flame*", 30000, 45000, 167, 169,
          "0.33s", 1000, 0, "Ground, Air", "Magic",
          "Overwhelming Arcane - Attacks bounce up to 4 times and increases mana by 5 per target hit, up to 500 mana. "
          "The damage dealt is increased by 2% for every 1% mana, up to 200%. 50% of the damage is dealt as "
          "Spell Damage. The mana of Arcane Orb is decreased by 20 every second.")
]


@bot.command(name="leaderboard", help="Prints the current leaderboard from the bot's local files")
async def leaderboard(ctx):
    file = open(parse_leaderboard(
        os.environ['USERPROFILE'] + "\\Documents\\Warcraft III\\CustomMapData\\LTWR\\Data50\\leaderboard_dump.txt"))
    response = file.readlines()
    response1 = ""
    response2 = "`"
    for line in response[:51]:
        response1 += line

    response1 += "`"

    for line in response[51:]:
        response2 += line

    await ctx.send(response1)
    await ctx.send(response2)


@bot.command(name="tower")
async def get_tower(ctx, tower_name):
    response = ""
    if tower_name == "list":
        for t in towers:
            response += t.name + ", "

    else:
        for t in towers:
            if tower_name.lower().replace(" ", "") == t.name.lower().replace(" ", ""):
                response = tower_to_string(t)
                break
            elif tower_name.lower().replace(" ", "") in t.name.lower().replace(" ", ""):
                response += tower_to_string(t)

    if response == "":
        response = "Tower not found"
    if len(response) > 2000:
        response = "Too many towers found, try a more specific term."
    await ctx.send(response)


@bot.command(name="creep")
async def get_creep(ctx, creep_name):
    response = "Creep not found"
    if creep_name == "list":
        for c in creep_data:
            response += c["CREEP"] + ", "
    else:
        response = get_creep_data(creep_name)

    if response == "":
        response = "Creep not found"
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
                + "\nTargets: " + t.targets + "\nAbility: " + t.ability_text + "\n\n"
    return response


def get_creep_data(creep_name):
    creep_string = ""
    for creep in creep_data:
        if creep_name.lower().replace(" ", "") == creep["CREEP"].lower().replace(" ", ""):
            print("match")
            creep_string = "**" + creep["CREEP"] + "** *(Version " + creep_data_version + ")*\nTier: " + \
                           str(creep["TIER"]) + "\nCost: " + str(creep["GOLD COST"]) + "\nIncome: " + \
                           str(creep["INCOME"]) + "\nBounty: " + str(creep["BOUNTY"]) + "\nHealth: " + \
                           str(creep["HP"]) + "\nArmor: " + str(creep["ARMOR"]) + "\nArmor Type: " + \
                           creep["ARMOR TYPE"] + "\nMove speed: " + str(creep["MOVE SPEED"])
            break
        elif creep_name.lower().replace(" ", "") in creep["CREEP"].lower().replace(" ", ""):
            creep_string += "**" + creep["CREEP"] + "** *(Version " + creep_data_version + ")*\nTier: " + \
                            str(creep["TIER"]) + "\nCost: " + str(creep["GOLD COST"]) + "\nIncome: " + \
                            str(creep["INCOME"]) + "\nBounty: " + str(creep["BOUNTY"]) + "\nHealth: " + \
                            str(creep["HP"]) + "\nArmor: " + str(creep["ARMOR"]) + "\nArmor Type: " + \
                            creep["ARMOR TYPE"] + "\nMove speed: " + str(creep["MOVE SPEED"]) + "\n\n"

    return creep_string


def parse_leaderboard(file_name):
    file = open(file_name)
    print(datetime.now())
    new_file_name = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " LTW Leaderboard.txt"
    new_file = open(new_file_name, "x")
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
