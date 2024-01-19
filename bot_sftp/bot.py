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
cmdprefix = config.get("prefix")
token = config.get("token")

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(command_prefix=cmdprefix, activity=discord.Activity(type=discord.ActivityType.listening, name=f"{prefix}help"), intents=intents)


@bot.event

async def on_ready():

    print(f'Logged in as {bot.user.name}')

async def load_extension():
    try:
        await bot.load_extension('codserver')
    except Exception as e:
        print(f'Failed to load extension: {e}')

def run_bot():
    asyncio.get_event_loop().run_until_complete(load_extension())
    
    bot.run(token)

run_bot()
