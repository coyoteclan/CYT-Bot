import discord
from discord.ext import commands, tasks
import os
import json
import re
from codserver import CoDServer
import asyncio

global currentdir
currentdir = os.path.dirname(os.path.realpath(__file__))
settings_file = "config.json"
settings_file_path = os.path.join(currentdir, settings_file)

with open(settings_file_path, 'r') as file:
    config = json.load(file)
adminrole = config.get("adminrole")
ban_file_path = config.get("ban_file_path")
report_file_path = config.get("report_file_path")
guild_id = config.get("guild")
channel_id = config.get("channel")
cmdprefix = config.get("prefix")
token = config.get("token")

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(command_prefix=cmdprefix, activity=discord.Activity(type=discord.ActivityType.listening, name='+help'), intents=intents)

report_line_file = 'last_line_count.dat'
ban_line_file = 'ban_line_count.dat'

report_count_path = os.path.join(currentdir, report_line_file)
ban_count_path = os.path.join(currentdir, ban_line_file)

def read_last_line_count():
    try:
        with open(report_count_path, 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        with open(report_count_path, 'w') as file:
            file.write('0')
        return 0  
def save_last_line_count(count):
    with open(report_count_path, 'w') as file:
        file.write(str(count))

report_line_count = read_last_line_count()

def read_ban_line_count():
    try:
        with open(ban_count_path, 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        with open(ban_count_path, 'w') as file:
            file.write('0')
        return 0  
def save_ban_line_count(count):
    with open(ban_count_path, 'w') as file:
        file.write(str(count))

ban_line_count = read_ban_line_count()

@tasks.loop(seconds=10)
async def check_report_file(guild_id, channel_id):
    global report_line_count

    try:
        with open(report_file_path, 'r') as report_file:
            lines = report_file.readlines()
            current_line_count = len(lines)

        if current_line_count > report_line_count:
            new_reports = lines[report_line_count:]
            for line in new_reports:
                values = line.strip().split('%')
                details_str = f'`Reporter:` {remove_color_code(values[0])}\n`Reporter IP:` {values[1]}\n`Reported Player:`{remove_color_code(values[2])}\n`Reported Player IP:` {values[3]}\n`Reason:` {values[4]}\n'
                guild = bot.get_guild(int(guild_id))
                if guild:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        await channel.send(f'{adminrole}\n__**New Report:**__\n{details_str}')
                    else:
                        print(f'Channel not found in guild {guild_id}: {channel_id}')
                else:
                    print(f'Guild not found: {guild_id}')

            report_line_count = current_line_count
            save_last_line_count(current_line_count)
    except Exception as e:
        print(f'Error processing reports for guild {guild_id}, channel {channel_id}: {e}')

@tasks.loop(seconds=10)
async def check_ban_file(guild_id, channel_id):
    global ban_line_count

    try:
        with open(ban_file_path, 'r') as ban_file:
            lines = ban_file.readlines()
            current_ban_line_count = len(lines)

        if current_ban_line_count > ban_line_count:
            new_bans = lines[ban_line_count:]
            for line in new_bans:
                values = line.strip().split('%')
                details_str = f'`Admin:` {remove_color_code(values[1])}\n`Banneed Player:`{remove_color_code(values[2])}\n`Banned Player IP:` {values[0]}\n`Reason:` {values[5]}\n'
                guild = bot.get_guild(int(guild_id))
                if guild:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        await channel.send(f'__**New Ban:**__\n{details_str}')
                    else:
                        print(f'Channel not found in guild {guild_id}: {channel_id}')
                else:
                    print(f'Guild not found: {guild_id}')

            ban_line_count = current_ban_line_count
            save_ban_line_count(current_ban_line_count)
    except Exception as e:
        print(f'Error processing bans for guild {guild_id}, channel {channel_id}: {e}')

def remove_color_code(name):
	name = re.sub(r'\^\^([0-7]{2})|\^([0-7]{1})|\^', '', name)
	return name

@bot.event

async def on_ready():

    print(f'Logged in as {bot.user.name}')
    check_report_file.start(int(guild_id), int(channel_id))
    check_ban_file.start(int(guild_id), int(channel_id))

async def load_extension():
    try:
        await bot.load_extension('codserver')
    except Exception as e:
        print(f'Failed to load extension: {e}')

def run_bot():
    asyncio.get_event_loop().run_until_complete(load_extension())
    
    bot.run(token)

run_bot()