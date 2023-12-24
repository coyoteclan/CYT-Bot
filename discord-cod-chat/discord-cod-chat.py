import discord
from rcon import RCON
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

# Load configuration from config.json
import json
with open('config.json') as f:
    config = json.load(f)

SERVER_IP = config['SERVER_IP']
SERVER_PORT = config['SERVER_PORT']
SERVER_RCONPASS = config['SERVER_RCONPASS']
SERVER_GAMELOG_PATH = config['SERVER_GAMELOG_PATH']
CHANNEL_ID = config['CHANNEL_ID']
BOT_TOKEN = config['BOT_TOKEN']

# Ban words for message filtering
ban_words = {"@everyone": "", "@here": ""}

# Initialize Discord client and RCON connection
client = discord.Client()
rcon_client = RCON(server=SERVER_IP, password=SERVER_RCONPASS, port=SERVER_PORT)

# Players list for tracking joins and leaves
players = []

class GameLogEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Process new gamelog lines
        with open(SERVER_GAMELOG_PATH, 'r') as gamelog_file:
            for line in gamelog_file.readlines():
                process_chat_line(line)

def process_chat_line(line):
    # Parse chat message
    chat_line = line.split(":")
    jq_line = line.split(";")

    if chat_line[1] == "say":
        # Check for valid message format
        if len(chat_line) == 4:
            # Filter out ban words
            msg = chat_line[3]
            for word, replacement in ban_words.items():
                msg = msg.replace(word, replacement)

            # Remove color codes from player name
            user = chat_line[2].replace('^0', '').replace('^1', '').replace('^2', '').replace('^3', '').replace('^4', '').replace('^5', '').replace('^6', '').replace('^7', '')

            # Send message to Discord channel
            channel = client.get_channel(CHANNEL_ID)
            asyncio.run_coroutine_threadsafe(channel.send(f"**{user}**: {msg}"))

    # Player joined the server
    elif jq_line[1] == "J":
        if jq_line[2] not in players:
            players.append(jq_line[2])

            # Remove color codes from player name
            user = jq_line[2].replace('^0', '').replace('^1', '').replace('^2', '').replace('^3', '').replace('^4', '').replace('^5', '').replace('^6', '').replace('^7', '')

            # Send player join message to Discord channel
            channel = client.get_channel(CHANNEL_ID)
            asyncio.run_coroutine_threadsafe(channel.send(f"{user} joined the server"))

    # Player left the server
    elif jq_line[1] == "Q":
        if jq_line[2] in players:
            players.remove(jq_line[2])

            # Remove color codes from player name
            user = jq_line[2].replace('^0', '').replace('^1', '').replace('^2', '').replace('^3', '').replace('^4', '').replace('^5', '').replace('^6', '').replace('^7', '')

            # Send player leave message to Discord channel
            channel = client.get_channel(CHANNEL_ID)
            asyncio.run_coroutine_threadsafe(channel.send(f"{user} left the server"))

@client.event
async def on_ready():
    print("Fionn's CoD 1.1 DiscordSRV Python Alt")
    print("by CoYoTe' Clan*")

    # Start monitoring gamelog file for changes
    observer = Observer()
    observer.schedule(GameLogEventHandler(), SERVER_GAMELOG_PATH)
    observer.start()

    try:
        await client.start(BOT_TOKEN)
    except discord.errors.LoginFailure as e:
        print(f"Login failed: {e}")
