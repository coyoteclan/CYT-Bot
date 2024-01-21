import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
import requests
import json
import re
import os
import time
from tabulate import tabulate

currentdir = os.path.dirname(os.path.realpath(__file__))
servers_config_file = os.path.join(currentdir, "server_config.json")
settings_file = os.path.join(currentdir, "config.json")
with open(settings_file, 'r') as file:
    settings = json.load(file)
my_color = settings.get("embedcolor")
my_color = int(my_color[1:], 16)

class CoDServer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Get status of a server.")
    async def status(self, ctx, server):
        try:
            with open(servers_config_file, 'r') as server_cfg:
                server_config = json.load(server_cfg)
            saved_servers = server_config.keys()
            if server not in saved_servers:
                await ctx.reply(f"Server not saved. Saved servers: {', '.join(saved_servers)}")
                return
            server_info = server_config[server]
            srv_ip = server_info["ip"]
            srv_port = server_info["port"]
            
            server_url = f"https://cod.pm/server/{srv_ip}/{srv_port}"
            api_url = f"https://api.cod.pm/getstatus/{srv_ip}/{srv_port}"
            
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                server_info = data.get("serverinfo", {})
                player_info = data.get("playerinfo", [])
                get_ip = data.get("getip", {})
                
                hostname = server_info.get("sv_hostname", "N/A")
                hostname = re.sub(r'\s+|\u0001', ' ', hostname)
                hostname = remove_color_code(hostname)
                hostname = re.sub(r'\s+|\u0001', ' ', hostname)
                print(f"Status: {hostname}")
                map_name = server_info.get("mapname", "N/A")
                gametype = server_info.get("g_gametype", "N/A")
                maxclients = server_info.get("sv_maxclients")
                if gametype == "sd":
                    gametype = "Search and Destroy"
                elif gametype == "dm":
                    gametype = "Deathmatch"
                elif gametype == "tdm":
                    gametype = "Team Deathmatch"
                elif gametype == "br":
                    gametype = "Battle Royale"
                elif gametype == "gg":
                    gametype = "Gun Game"
                elif gametype == "ftag":
                    gametype = "Freezetag"
                elif gametype == "re":
                    gametype = "Retrieval"
                elif gametype == "bel":
                    gametype = "Behind Enemy Lines"
                elif gametype == "zom":
                    gametype = "Zombies"
                elif gametype == "jmp":
                    gametype = "Jump"
                stockmaps = ["mp_carentan", "mp_dawnville", "mp_brecourt", "mp_powcamp", "mp_harbor", "mp_railyard", "mp_matmata", "mp_hurtgen", "mp_chateau",  "mp_rocket", "mp_foy", "mp_pavlov"]
                if map_name in stockmaps:
                    map_image = f"https://cod.pm/mp_maps/stock/{map_name}.png"
                else:
                    map_image = f"https://cod.pm/mp_maps/stock/unknown.png"
                if get_ip:
                    location = get_ip.get("country_name", "N/A")
                else:
                    location = "N/A"
                embed = discord.Embed(title="Server Info", description=f"<t:{int(time.time())}:R>", color=my_color)
                embed.add_field(name="Server Name", value=f"[{hostname}]({server_url})", inline=True)
                embed.add_field(name="Gametype", value=f"{gametype}", inline=True)
                embed.add_field(name="Location", value=f"{location}", inline=True)
                embed.add_field(name="Map", value=f"{map_name}", inline=True)
                embed.set_image(url=map_image)
                if player_info:
                    players = f"{len(player_info)}/{maxclients}\n"
                    head = ['Player', 'Score', 'Ping']
                    rows = [[remove_color_code(player['name']), player['score'], player['ping']] for player in player_info]
                    table = tabulate(rows, head, tablefmt="grid")
                    players += f"```{table}```"
                    
                else:
                    players = f"0/{maxclients}"
                embed.add_field(name="Players Online", value=players, inline=False)
                await ctx.reply(embed=embed)
            else:
                await ctx.reply("Error fetching server info")
        except discord.Forbidden as e:
            await ctx.send(f"I don't have permissions to do that.")
        except FileNotFoundError:
            await ctx.reply("The config file does not exist.")
        except Exception as e:
            print(f"Error: {e}")
            
    @commands.command(description="Get a list of saved servers.")
    async def servers(self, ctx):
        try:
            with open(servers_config_file, 'r') as server_cfg:
                server_config = json.load(server_cfg)
            if server_config:
                list = "\n".join(server_config.keys())
                await ctx.reply(f"__**Saved Servers**__:\n {list}")
            else:
                await ctx.reply("No saved servers... yet")
        except Exception as e:
            print(f"{e}")
    
    @commands.command(description="Add a new server.")
    async def addserver(self, ctx, name, ip, port):
        try:
            with open(servers_config_file, 'r') as server_cfg:
                server_config = json.load(server_cfg)
        except FileNotFoundError:
            server_config = {}
        server_config[name] = {'ip': ip, 'port': port}
        with open(servers_config_file, 'w') as server_cfg:
            json.dump(server_config, server_cfg, indent=4)
        await ctx.reply(f"Server {name} added successfully!")
    
    @commands.command()
    async def removeserver(self, ctx, name):
        try:
            with open(servers_config_file, 'r') as server_cfg:
                server_config = json.load(server_cfg)
            if name in server_config:
                del server_config[name]
                with open(servers_config_file, 'w') as server_cfg:
                    json.dump(server_config, server_cfg, indent=4)
                await ctx.reply(f"Removed Server: {name}")
            else:
                await ctx.reply(f"Server: {name} is not saved.")
        except Exception as e:
            print(e)
    
    @commands.command(description="Pin status in this channel")
    async def pin_status(self, ctx):
        pinned_messages = await ctx.channel.pins()
        for message in pinned_messages:
            if message.author == ctx.guild.me and "Server Info" in message.embeds[0].title:
                await ctx.reply("There is already a pinned status message in this channel.")
                return
        with open(servers_config_file, 'r') as server_cfg:
            server_config = json.load(server_cfg)
        if server_config:
            options = [discord.SelectOption(label=entry, value=entry) for entry in server_config.keys()]
        select = Select(placeholder="Choose a server", options=options)
        async def my_call(interaction):
            selected_server = interaction.data["values"][0]
            with open(servers_config_file, 'r') as server_cfg:
                server_config = json.load(server_cfg)
            server_info = server_config[selected_server]
            srv_ip = server_info["ip"]
            srv_port = server_info["port"]
            
            server_url = f"https://cod.pm/server/{srv_ip}/{srv_port}"
            api_url = f"https://api.cod.pm/getstatus/{srv_ip}/{srv_port}"
            
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                server_info = data.get("serverinfo", {})
                player_info = data.get("playerinfo", [])
                get_ip = data.get("getip", {})
                
                hostname = server_info.get("sv_hostname", "N/A")
                hostname = re.sub(r'\s+|\u0001', ' ', hostname)
                hostname = remove_color_code(hostname)
                hostname = re.sub(r'\s+|\u0001', ' ', hostname)
                map_name = server_info.get("mapname", "N/A")
                gametype = server_info.get("g_gametype", "N/A")
                maxclients = server_info.get("sv_maxclients")
                if gametype == "sd":
                    gametype = "Search and Destroy"
                elif gametype == "dm":
                    gametype = "Deathmatch"
                elif gametype == "tdm":
                    gametype = "Team Deathmatch"
                elif gametype == "br":
                    gametype = "Battle Royale"
                elif gametype == "gg":
                    gametype = "Gun Game"
                elif gametype == "ftag":
                    gametype = "Freezetag"
                elif gametype == "re":
                    gametype = "Retrieval"
                elif gametype == "bel":
                    gametype = "Behind Enemy Lines"
                elif gametype == "zom":
                    gametype = "Zombies"
                elif gametype == "jmp":
                    gametype = "Jump"
                stockmaps = ["mp_carentan", "mp_dawnville", "mp_brecourt", "mp_powcamp", "mp_harbor", "mp_railyard", "mp_matmata", "mp_hurtgen", "mp_chateau",  "mp_rocket", "mp_foy", "mp_pavlov"]
                if map_name in stockmaps:
                    map_image = f"https://cod.pm/mp_maps/stock/{map_name}.png"
                else:
                    map_image = f"https://cod.pm/mp_maps/stock/unknown.png"
                if get_ip:
                    location = get_ip.get("country_name", "N/A")
                else:
                    location = "N/A"
                embed = discord.Embed(title="Server Info", description=f"Last Updated: <t:{int(time.time())}:R>", color=0x00ff00)
                embed.add_field(name="Server Name", value=f"[{hostname}]({server_url})", inline=True)
                embed.add_field(name="Gametype", value=f"{gametype}", inline=True)
                embed.add_field(name="Location", value=f"{location}", inline=True)
                embed.add_field(name="Map", value=f"{map_name}", inline=True)
                embed.set_image(url=map_image)
                if player_info:
                    players = f"{len(player_info)}/{maxclients}\n"
                    head = ['Player', 'Score', 'Ping']
                    rows = [[remove_color_code(player['name']), player['score'], player['ping']] for player in player_info]
                    table = tabulate(rows, head, tablefmt="grid")
                    players += f"```{table}```"
                    
                else:
                    players = f"0/{maxclients}"
                embed.add_field(name="Players Online", value=players, inline=False)
                print(f"Status: {hostname}")
                await interaction.response.edit_message(embed=embed, view=view)
                @tasks.loop(minutes=10.0)
                async def refresh_status():
                    pinned_messages = await ctx.channel.pins()
                    for message in pinned_messages:
                        if message.author == ctx.guild.me and "Server Info" in message.embeds[0].title:
                            await message.unpin()
                            await message.delete()
                            status = await ctx.send(embed=embed, view=view)
                            await status.pin()
                if not refresh_status.is_running():
                    refresh_status.start()
            else:
                return
        select.callback = my_call
        view = View()
        view.add_item(select)
        message = await ctx.reply(view=view)
        await message.pin()
    
    @commands.command(aliases=['ms'], description="Get a list of active servers for a game.")
    async def masterlist(self, ctx, game: str, version: str):
        try:
            ms_url = f"https://api.cod.pm/masterlist/{game}/{version}"
            response = requests.get(ms_url)
            data = response.json()
            if "servers" not in data:
                await ctx.send("Failed to retrieve masterlist.")
                return
            
            servers = data["servers"]
            embed = discord.Embed(title=f"Masterlist - {game} {version}", color=0x00ff00)
            for server in servers:
                server_name = server["sv_hostname"].replace('/u0001', '')
                if server["clients"] > 0:
                    embed.add_field(
                        name=server_name,
                        value=f"Map: {server['mapname']}\nPlayers: {server['clients']}/{server['sv_maxclients']}",
                        inline=False
                    )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("An error occurred while fetching masterlist.")
            print(f"Error: {e}")

def remove_color_code(name):
	name = re.sub(r'\^\^([0-7]{2})|\^([0-7]{1})|\^', '', name)
	return name
def decorate(string: str):
    string = f"__**{string}**__"
    return string

async def setup(bot):
    await bot.add_cog(CoDServer(bot))
