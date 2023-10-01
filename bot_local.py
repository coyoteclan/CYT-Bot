# Bot made for CoYoTe' Clan*

import discord
from discord.ext import commands, tasks
import asyncio
import os
import requests
import re

# Replace with your admin role. In this way: <@&"role id">
adminrole = '<@&1131572747076632687>'
#Ban file path including filename
ban_file_path = 'F:/bot/miscmod_bans.dat'
#Reports file path including filename
report_file_path = 'F:/bot/miscmod_reports.dat'
def read_last_line_count():
    try:
        with open('last_line_count.dat', 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        # Create the file if it doesn't exist and initialize with 0
        with open('last_line_count.dat', 'w') as file:
            file.write('0')
        return 0  # Return 0 since the file was just created
def save_last_line_count(count):
    with open('last_line_count.dat', 'w') as file:
        file.write(str(count))
last_line_count = read_last_line_count()

def remove_color_code(player_name):
    # Replace double '^' with a special character temporarily
    player_name = re.sub(r'\^\^([0-7]{2})|\^([0-7]{1})|\^', '', player_name)

    return player_name

@tasks.loop(seconds=10)  # Adjust the interval as needed (e.g., every 10 seconds)
async def check_report_file(guild_id, channel_id):
    global last_line_count

    try:
        # Read the current line count in the report file
        with open(report_file_path, 'r') as report_file:
            lines = report_file.readlines()
            current_line_count = len(lines)

        # Check if there are new lines (reports)
        if current_line_count > last_line_count:
            new_reports = lines[last_line_count:]
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

            last_line_count = current_line_count
            # Save the last processed line count to the file
            save_last_line_count(current_line_count)
    except Exception as e:
        print(f'Error processing reports for guild {guild_id}, channel {channel_id}: {e}')

# Specify Guild and Channel ID
guild_channel_ids = [
    {'guild_id': '1131571343930951444', 'channel_id': '1150065592456458311'},
]

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix='+', activity=discord.Activity(type=discord.ActivityType.listening, name='+help'), intents=intents)

# Define server configurations with IP and port
server_configs = {
    "sd": {"ip": "65.109.65.23", "port": "11570"},
    "dm": {"ip": "65.109.65.23", "port": "8770"},  # Example: Add more servers as needed
    "tdm": {"ip": "65.109.65.23", "port": "11043"},
    "ftag": {"ip": "65.109.65.23", "port": "7914"},
    "zom": {"ip": "65.109.65.23", "port": "5567"},
	"rocks": {"ip": "78.46.65.243", "port": "6420"},

}

# Define map image URLs
map_images = {
    "zh_king": "https://raw.githubusercontent.com/Kazam3766/mapimages/main/zh_king.png",
    "mp_harbor": "https://cod.pm/mp_maps/stock/mp_harbor.png",
    "mp_carentan": "https://cod.pm/mp_maps/stock/mp_carentan.png",
    "mp_brecourt": "https://cod.pm/mp_maps/stock/mp_brecourt.png",
    "mp_rocket": "https://cod.pm/mp_maps/stock/mp_rocket.png",
    "mp_depot": "https://cod.pm/mp_maps/stock/mp_depot.png",
    "mp_railyard": "https://cod.pm/mp_maps/stock/mp_railyard.png",
    "training_outside": "https://raw.githubusercontent.com/Kazam3766/mapimages/main/training_outside.png",
    "mp_stalingrad": "https://cod.pm/mp_maps/stock/mp_stalingrad.png",
    "mp_dawnville": "https://cod.pm/mp_maps/stock/mp_dawnville.png",
    "mp_tigertown": "https://cod.pm/mp_maps/stock/mp_tigertown.png",
    "mp_bocage": "https://cod.pm/mp_maps/stock/mp_bocage.png",
    
    # Add more map-image pairs as needed
}

# Define the image for unknown maps
unknown_map = "https://cod.pm/mp_maps/stock/unknown.png"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Start the background tasks for each guild and channel
    for entry in guild_channel_ids:
        check_report_file.start(int(entry['guild_id']), int(entry['channel_id']))

@bot.command()
async def status(ctx, server_type):
    try:
        valid_server_types = server_configs.keys()

        if server_type not in valid_server_types:
            await ctx.reply(f"Invalid server type. Available types: {', '.join(valid_server_types)}")
            return

        server_info = server_configs[server_type]
        ip = server_info["ip"]
        port = server_info["port"]

        # Create the URL to direct to
        server_url = f"https://cod.pm/server/{ip}/{port}"
		
        api_url = f"https://api.cod.pm/getstatus/{ip}/{port}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            server_info = data.get("serverinfo", {})
            player_info = data.get("playerinfo", [])

            server_name = server_info.get("sv_hostname", "N/A")
            map_name = server_info.get("mapname", "N/A")

            # Create an embed with server info and player info
            embed = discord.Embed(title="Server Info", color=0x00ff00)
            embed.add_field(name="Server Name", value=f"[{server_name}]({server_url})", inline=False)
            embed.add_field(name="Map Name", value=map_name, inline=False)

            if map_name in map_images:
                map_image_url = map_images[map_name]
            else:
                map_image_url = unknown_map

            embed.set_thumbnail(url=map_image_url)

            if player_info:
                # Remove '^' and numbers 0-7 from player names
                cleaned_player_names = [remove_color_code(player['name']) for player in player_info]
                player_list = "\n".join([f"**{cleaned_name}** - Score: {player['score']}, Ping: {player['ping']}" for cleaned_name, player in zip(cleaned_player_names, player_info)])
                embed.add_field(name="Players Online", value=player_list, inline=False)

            await ctx.reply(embed=embed)
        else:
            await ctx.reply("Failed to retrieve server info.")

    except Exception as e:
        await ctx.reply("An error occurred while fetching server info.")
        print(f'Error fetching server info: {e}')



@bot.command(aliases=['bl', 'blist'], description="Display the list of banned players.")
async def banlist(ctx):
    try:
        with open(ban_file_path, 'r') as ban_file:
            lines = ban_file.readlines()
            ban_list = '\n'.join([remove_color_code(line.strip().split('%')[2]) for line in lines])
            await ctx.reply(f'__**Banned Players:**__`\n{ban_list}`')
    except FileNotFoundError:
        await ctx.reply('`The ban list file was not found.`')

@bot.command(aliases=['bd', 'bdetails'], description="Display details of a banned player.")
@commands.has_permissions(manage_guild=True)
async def ban_details(ctx, player_name: str):
    try:
        with open('miscmod_bans.dat', 'r') as ban_file:
            lines = ban_file.readlines()
            matches = []
            for line in lines:
                values = line.strip().split('%')
                if player_name.lower() in values[2].lower():
                    time_in_seconds = int(values[3])
                    if time_in_seconds == 0:
                        time_description = "Permanent"
                    else:
                        time_in_hours = convert_seconds_to_hours(time_in_seconds)
                        time_description = f"{time_in_hours} hours"                    
                    matches.append(values)
            if matches:
                details_str = "\n\n".join([f'`Player Name:` {remove_color_code(values[2])}\n`Banned IP:` {values[0]}\n`Reason:` {values[5]}\n`Admin:` {values[1]}\n`Time: `{time_description}' for values in matches])
                await ctx.reply(f'__**Match(es) found:**__\n{details_str}')
            else:
                await ctx.reply('`No matching players found in the ban list.`')
    except FileNotFoundError:
        await ctx.reply('`The ban list file was not found.`')

def convert_seconds_to_hours(seconds):
    if seconds == 0:
        return 0
    hours = seconds // 3600
    return hours

@bot.command(aliases=['rlist'], description="Show the reports")
async def reports(ctx):
    try:
        with open('miscmod_reports.dat', 'r') as report_file:
            lines = report_file.readlines()
            reports = [line.strip().split('%') for line in lines]
            reported_players = [remove_color_code(report[2]) for report in reports]
            reported_players_str = '\n'.join(reported_players)
            await ctx.reply(f'__**Reported Players:**__\n`{reported_players_str}`')
    except FileNotFoundError:
        await ctx.reply('`The report list file was not found.`')

@bot.command(aliases=['rdetails', 'rd'], description="Show report details.")
@commands.has_permissions(manage_guild=True)
async def report_details(ctx, player_name: str):
    try:
        with open(report_file_path, 'r') as report_file:
            lines = report_file.readlines()
            matches = []
            for line in lines:
                values = line.strip().split('%')
                if player_name.lower() in values[2].lower():
                    matches.append(values)
            if matches:
                details_str = "\n\n".join([f'`Reporter:` {remove_color_code(values[0])}\n`Reporter IP:` {values[1]}\n`Reported Player:` {remove_color_code(values[2])}\n`Reported Player IP:` {values[3]}\n`Reason:` {values[4]}\n' for values in matches])
                await ctx.reply(f'__**Match(es) found:**__\n{details_str}')
            else:
                await ctx.reply('`No matching reports found.`')
    except FileNotFoundError:
        await ctx.reply('`The report list file was not found.`')


# Helper function to convert time to seconds
def convert_to_seconds(time):
    unit = time[-1]
    value = int(time[:-1])

    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    else:
        return 0  # Permanent ban

@bot.command()
async def add_ban(ctx, ip, name, reason, ban_time):
    try:
        # Get admin (Discord username)
        admin = ctx.author.name

        # Check if the ban_time is valid
        if not ban_time[:-1].isdigit() or ban_time[-1] not in ['s', 'm', 'h', 'd', '0']:
            await ctx.reply("Invalid ban time format. Use digits followed by 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days, or '0' for permanent.")
            return

        # Convert ban_time to seconds
        ban_time_seconds = convert_to_seconds(ban_time)

        # Read the current contents of the remote file as bytes
        with open(ban_file_path, 'rb') as remote_file:
            existing_content = remote_file.read()

        # Append the new line to the existing content
        ban_line = f"1.1.1.1%{admin}%{name}%{ban_time_seconds}%167548%{reason}\n"
        updated_content = existing_content + ban_line.encode('utf-8')

        # Write the updated content back to the remote file
        with open(ban_file_path, 'wb') as remote_file:
            remote_file.write(updated_content)


        await ctx.reply(f"Banned: {name} ({ip}) For {ban_time} - Reason: {reason}")

        print('Ban added successfully')
    except Exception as e:
        await ctx.reply("An error occurred while adding the ban.")
        print(f'Error adding ban: {e}')



@bot.command(description="Unban a Player.")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def unban(ctx, *, name):
    try:
        # Inform user to wait
        wait_message = await ctx.reply("Please wait...")
        

        # Read the current contents of the remote file
        with open(ban_file_path, 'r') as remote_ban_file:
            lines = remote_ban_file.readlines()

        # Filter out the banned user's line
        lines = [line for line in lines if name.lower() not in line.lower()]

        # Write the modified lines back to the remote file
        with open(ban_file_path, 'w') as ban_file:
            ban_file.writelines(lines)


        # Delete the wait message
        await wait_message.edit(content="Successfully Unbanned: " + name)

        print('User unbanned successfully')
    except Exception as e:
        await ctx.reply("An error occurred while unbanning the user.")
        print(f'Error unbanning user: {e}')

@bot.command(aliases=['cr'], description="Clear the reports file.")
@commands.has_permissions(manage_guild=True)
async def clear_reports(ctx):
    try:
        # Truncate the content of the reports file
        with open(report_file_path, 'w') as remote_file:
            remote_file.truncate(0)

        await ctx.reply("Reports file cleared successfully")

        print('Reports file cleared')
    except Exception as e:
        await ctx.reply("An error occurred while clearing the reports file.")
        print(f'Error clearing reports file: {e}')

bot.run('your token')