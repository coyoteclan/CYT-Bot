# Add Cython imports
from os import path
import json
from termcolor import termcolor
import requests
from re import sub
from math import ceil
from tabulate import tabulate
import cython

from discord import Embed
from discord.ui import Button, View
from discord import ButtonStyle

lbreak:str = "---------------------------------------------------"

cfgFile:str = path.join(path.dirname(path.realpath(__file__)), "config.json")

loadedServers = {}
config = {}

# Load configuration file
with open(cfgFile, 'r') as file:
    try:
        config = json.load(file)
    except Exception as e:
        print(f"Error loading config: {e}")

embedColor:cython.int = int(config.get("embedcolor")[1:], 16)
errColor:cython.int = int("e60000", 16)

#@locals()
def loadServers(guild_id:str) -> None:
    """Load servers from a JSON file."""
    global loadedServers
    serversFile = path.join(path.dirname(path.realpath(__file__)), "servers", f"{guild_id}.json")
    try:
        with open(serversFile, 'r') as f:
            loadedServers[guild_id] = json.load(f)
            f.close()
    except FileNotFoundError:
        open(serversFile, 'w').close()
        saveServers(guild_id)
    except Exception as e:
        print(f"Couldn't load saved servers: {e}")

#loadServers()

def saveServers(guild_id:str) -> None:
    """Save servers to JSON file."""
    serversFile = path.join(path.dirname(path.realpath(__file__)), "servers", f"{guild_id}.json")
    try:
        with open(serversFile, 'w') as f:
            json.dump(loadedServers[guild_id], f, indent=4)
            f.close()
    except Exception as e:
        print(f"Couldn't save servers: {e}")

#@locals(string=str)
def red(string:str) -> cython.char:
    return termcolor.colored(string, "red")

#@locals(string=str)
def green(string:str) -> cython.char:
    return termcolor.colored(string, "green")

#@locals(string=str)
def blue(string:str) -> cython.char:
    return termcolor.colored(string, "blue")

#@locals(string=str)
def cyan(string:str) -> cython.char:
    return termcolor.colored(string, "cyan")

#@locals(string=str)
def yellow(string:str) -> cython.char:
    return termcolor.colored(string, "yellow")

#@locals(name=str)
def monotone(name:str) -> cython.char:
    return sub(r'\^\^([0-7]{2})|\^([0-7]{1})|\^', '', name)

#@locals(string=str)
def BU(string:str) -> cython.char:
    return f"__**{string}**__"

#@locals(hostname=str)
def processHostname(hostname:str) -> cython.char:
    s = monotone(sub(r'\s+|[^\x00-\x7F]+|[\x00-\x1F\x7F]|`|``|```', ' ', hostname))
    if s == "":
        s = "Unnamed Server"
    return s

#@locals(gametype=str)
def gt_name(gametype:str) -> cython.char:
    gametype = monotone(gametype).lower()
    if gametype == "sd":
        return "Search & Destroy"
    elif gametype == "dm":
        return "Deathmatch"
    elif gametype == "tdm":
        return "Team Deathmatch"
    elif gametype == "br":
        return "Battle Royale"
    elif gametype == "gg":
        return "Gun Game"
    elif gametype == "ftag":
        return "Freezetag"
    elif gametype == "re":
        return "Retrieval"
    elif gametype == "bel":
        return "Behind Enemy Lines"
    elif gametype == "zom":
        return "Zombies"
    elif gametype == "jmp":
        return "Jump"
    elif gametype == "hq":
        return "Headquaters"
    elif gametype == "bas":
        return "Base Assault"
    elif gametype == "dom":
        return "Domination"
    else:
        return gametype

#@locals(ip=str, port=int)
async def getSVInfo(ip:str, port:cython.int) -> list:
    """Fetch server information from an API."""
    url:str = f"https://api.cod.pm/getstatus/{ip}/{port}"
    notAvail:str = "N/A"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            server_info = data.get("serverinfo", {})
            player_info = data.get("playerinfo", [])
            geoip = data.get("geoip", {})

            hostname:str = processHostname(server_info.get("sv_hostname", notAvail))
            if len(hostname) > 25:
                hostname = hostname[:24]
            map:str = server_info.get("mapname", notAvail)
            maxclients:str = server_info.get("sv_maxclients", notAvail)
            gametype:str = gt_name(server_info.get("g_gametype", notAvail))
            map_image:str = "https://cod.pm/mp_maps/" + data.get("mapimage", "unknown.png")

            if geoip:
                location:str = geoip.get("country_name", notAvail)
            else:
                location:str = notAvail
            
            players:str = "0/0\n"
            playerInfoChunks = {}
            if player_info:
                players = f"{len(player_info)}/{maxclients}\n"
                head = ['Player', 'Score', 'Ping']

                chunkSize = 6
                chunks = [player_info[i:i + chunkSize] for i in range(0, len(player_info), chunkSize)]
                for idx, chunk in enumerate(chunks):
                    rows = [[monotone(player['name']), player['score'], player['ping']] for player in chunk]
                    table = tabulate(rows, headers=head, tablefmt='grid')
                    playerInfoChunks[f"Players (Page {idx + 1})"] = f"```{table}```"
                
            return [hostname, map, gametype, location, map_image, players, playerInfoChunks]
    except Exception as e:
        print(f"Error in getSVInfo: {e}")

from typing import Tuple

def errEmbed(message:str) -> Tuple[Embed, View]:
    embed = Embed()
    view = View()

    embed.title = "ERROR"
    embed.color = errColor
    if len(message) != 0:
        embed.add_field(name="Error", value=message)

    reportButton = Button(style=ButtonStyle.red, label="Notify Developer", url="https://discord.com/users/932181218936651827")
    view.add_item(reportButton)
    
    return embed, view

def ms_embed(game:str, version:str) -> Tuple[Embed, View]:
    embed = Embed()
    view = View()
    try:
        ms_url:str = f"https://api.cod.pm/masterlist/{game}/{version}"
        response = requests.get(ms_url)
        data = response.json()
        if "servers" not in data:
            return errEmbed("Failed to retrieve masterlist.")
        
        servers = data["servers"]
        embed.title = f"Masterlist - {game} {version}"
        embed.color = embedColor
        if len(servers) >= 10:
            servers = servers[:10]
        for server in servers:
            server_name:str = processHostname(processHostname(server["sv_hostname"]))
            if len(server_name) > 25:
                server_name = server_name[:25]
            if server["clients"] > 0:
                map_text:str = BU("Map:")
                players_text:str = BU("Players:") 
                embed.add_field(name=server_name, value=f"{map_text} {server['mapname']}\n{players_text} {server['clients']}/{server['sv_maxclients']}", inline=False)
        
        return embed, view
    except Exception as e:
        print(e)
        return errEmbed("")

