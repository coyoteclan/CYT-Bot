# Bot made by CoYoTe' Clan*

import json
import re
import discord
from discord.ext import commands, tasks
import asyncio
import paramiko
import os
import requests

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
bot = commands.Bot(command_prefix='+', activity=discord.Activity(type=discord.ActivityType.listening, name='+help'), intents=intents)

# Set SFTP server details
sftp_host = ''
sftp_port = 0
sftp_username = ''
sftp_password = ''

# config file name
config_file = 'server_config.json'

current_directory = os.path.dirname(os.path.realpath(__file__))

config_file_path = os.path.join(current_directory, config_file)

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

# Function to remove '^' and numbers 0-7 from player names
def remove_color_code(player_name):
    # Replace double '^' with a special character temporarily
    player_name = re.sub(r'\^\^([0-7]{2})|\^([0-7]{1})|\^', '', player_name)

    return player_name

  
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def status(ctx, server):
    try:
        with open(config_file_path, 'r') as server_configs_file:
            server_configs = json.load(server_configs_file)

        saved_servers = server_configs.keys()

        if server not in saved_servers:
            await ctx.send(f"Invalid server type. Available types: {', '.join(saved_servers)}")
            return

        server_info = server_configs[server]
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

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to retrieve server info.")

    except Exception as e:
        await ctx.send("An error occurred while fetching server info.")
        print(f'Error fetching server info: {e}')



@bot.command(aliases=['bl', 'blist'], description="Display the list of banned players.")
async def banlist(ctx):
    try:
        with open('miscmod_bans.dat', 'r') as ban_file:
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
                details_str = "\n\n".join([f'`Player Name:` {remove_color_code(values[2])}\n`Banned IP:` {values[0]}\n`Reason:` {values[5]}\n`Admin:` {remove_color_code(values[1])}\n`Time: `{time_description}' for values in matches])
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
        with open('miscmod_reports.dat', 'r') as report_file:
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


@bot.command(aliases=['upbans', 'upb'], description="Update the bans file.")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def update_bans(ctx):
    try:
        # Inform user to wait
        wait_message = await ctx.reply("Please wait, updating bans...")

        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to SFTP server with specified host key
        client.connect(sftp_host, port=sftp_port, username=sftp_username, password=sftp_password)

        # Create an SFTP session
        sftp = client.open_sftp()

        # Change remote directory
        sftp.chdir('/main')

        # Download the file
        remote_ban_file_path = 'miscmod_bans.dat'
        local_file_path = os.path.join(os.path.dirname(__file__), remote_ban_file_path)
        sftp.get(remote_ban_file_path, local_file_path)

        # Close the SFTP session
        sftp.close()

        # Inform user about successful update
        await wait_message.edit(content="Updated Successfully")

        print('Download successful')
    except Exception as e:
        await wait_message.edit(content="An error occurred while updating bans.")
        print(f'Error downloading file: {e}')
    finally:
        # Close the SSH client
        client.close()

@bot.command(aliases=['upreports', 'upr'], description="Update the reports file.")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def update_reports(ctx):
    try:
        # Inform user to wait
        wait_message = await ctx.reply("Please wait, updating reports...")

        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to SFTP server with specified host key
        client.connect(sftp_host, port=sftp_port, username=sftp_username, password=sftp_password)

        # Create an SFTP session
        sftp = client.open_sftp()

        # Change remote directory
        sftp.chdir('/main')

        # Download the file
        remote_report_file_path = 'miscmod_reports.dat'
        local_file_path = os.path.join(os.path.dirname(__file__), remote_report_file_path)
        sftp.get(remote_report_file_path, local_file_path)

        # Close the SFTP session
        sftp.close()

        # Inform user about successful update
        await wait_message.edit(content="Updated Successfully")

        print('Download successful')
    except Exception as e:
        await wait_message.edit(content="An error occurred while updating reports.")
        print(f'Error downloading file: {e}')
    finally:
        # Close the SSH client
        client.close()

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
@commands.has_permissions(manage_guild=True)
async def add_ban(ctx, ip, name, reason, ban_time):
    try:
        # Get admin (Discord username)
        admin = ctx.author.name

        # Check if the ban_time is valid
        if not ban_time[:-1].isdigit() or ban_time[-1] not in ['s', 'm', 'h', 'd', '0']:
            await ctx.send("Invalid ban time format. Use digits followed by 's' for seconds, 'm' for minutes, 'h' for hours, 'd' for days, or '0' for permanent.")
            return

        # Convert ban_time to seconds
        ban_time_seconds = convert_to_seconds(ban_time)

        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to SFTP server with specified host key
        client.connect(sftp_host, port=sftp_port, username=sftp_username, password=sftp_password)

        # Create an SFTP session
        sftp = client.open_sftp()

        # Change remote directory
        sftp.chdir('/main')
        remote_file_path = 'miscmod_bans.dat'

        # Read the current contents of the remote file as bytes
        with sftp.file(remote_file_path, 'rb') as remote_file:
            existing_content = remote_file.read()

        # Append the new line to the existing content
        ban_line = f"1.1.1.1%{admin}%{name}%{ban_time_seconds}%167548%{reason}\n"
        updated_content = existing_content + ban_line.encode('utf-8')

        # Write the updated content back to the remote file
        with sftp.file(remote_file_path, 'wb') as remote_file:
            remote_file.write(updated_content)

        # Close the SFTP session
        sftp.close()
        await ctx.reply(f"Banned: {name} ({ip}) For {ban_time} - Reason: {reason}")

        print('Ban added successfully')
    except Exception as e:
        await ctx.send("An error occurred while adding the ban.")
        print(f'Error adding ban: {e}')
    finally:
        # Close the SSH client
        client.close()


@bot.command(description="Unban a Player.")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_guild=True)
async def unban(ctx, *, name):
    try:
        # Inform user to wait
        wait_message = await ctx.reply("Please wait...")
        
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to SFTP server with specified host key
        client.connect(sftp_host, port=sftp_port, username=sftp_username, password=sftp_password)

        # Create an SFTP session
        sftp = client.open_sftp()

        # Change remote directory
        sftp.chdir('/main')
        remote_ban_file_path = 'miscmod_bans.dat'

        # Read the current contents of the remote file
        with sftp.file(remote_ban_file_path, 'r') as remote_ban_file:
            lines = remote_ban_file.readlines()

        # Filter out the banned user's line
        lines = [line for line in lines if name.lower() not in line.lower()]

        # Write the modified lines back to the remote file
        with sftp.file(remote_ban_file_path, 'w') as remote_ban_file:
            remote_ban_file.writelines(lines)

        # Close the SFTP session
        sftp.close()

        # Delete the wait message
        await wait_message.edit(content="Successfully Unbanned: " + name)

        print('User unbanned successfully')
    except Exception as e:
        await ctx.reply("An error occurred while unbanning the user.")
        print(f'Error unbanning user: {e}')
    finally:
        # Close the SSH client
        client.close()

@bot.command(aliases=['cr'], description="Clear the reports file.")
@commands.has_permissions(manage_guild=True)
async def clear_reports(ctx):
    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to SFTP server with specified host key
        client.connect(sftp_host, port=sftp_port, username=sftp_username, password=sftp_password)

        # Create an SFTP session
        sftp = client.open_sftp()

        # Change remote directory
        sftp.chdir('/main')
        remote_reports_path = 'miscmod_reports.dat'

        # Truncate the content of the reports file
        with sftp.file(remote_reports_path, 'w') as remote_file:
            remote_file.truncate(0)

        # Close the SFTP session
        sftp.close()

        await ctx.reply("Reports file cleared successfully")

        print('Reports file cleared')
    except Exception as e:
        await ctx.send("An error occurred while clearing the reports file.")
        print(f'Error clearing reports file: {e}')
    finally:
        # Close the SSH client
        client.close()

@bot.command(aliases=['newserver'], description="Add a new server")
@commands.has_permissions(manage_guild=True)
async def addserver(ctx, name, ip, port):
    try:
        with open(config_file_path, 'r') as server_configs_file:
            server_configs = json.load(server_configs_file)
    except FileNotFoundError:
        server_configs = {}
    server_configs[name] = {'ip': ip, 'port': port}

    with open(config_file_path, 'w') as server_configs_file:
        json.dump(server_configs, server_configs_file, indent=4)
    await ctx.reply(f"Server '{name}' added successfully!")

@bot.command(aliases=['delserver'], description="Remove a server.")
@commands.has_permissions(manage_guild=True)
async def removeserver(ctx, name):
    try:
        with open(config_file_path, 'r') as server_configs_file:
            server_configs = json.load(server_configs_file)
            if name in server_configs:
                del server_configs[name]
                with open(config_file_path, 'w') as server_configs_file:
                    json.dump(server_configs, server_configs_file, indent=4)
                await ctx.reply(f"Removed server: '{name}'")
            else:
                await ctx.reply(f"Server '{name}' not in saved servers.")
    except Exception as e:
        await ctx.reply(f"An error occurred while removing the server.")
        print(f"Error removing server: {e}")

@bot.command(aliases=['listservers', 'savedservers'], description="List saved servers.")
@commands.has_permissions(send_messages=True)
async def servers(ctx):
    try:
        with open(config_file_path, 'r') as server_configs_file:
            server_config = json.load(server_configs_file)
        if server_config:
            list = "\n".join(server_config.keys())
            await ctx.reply(f"__**Saved Servers**__:\n {list}")
        else:
            await ctx.reply(f"No servers saved... yet.")
    except Exception as e:
        await ctx.reply(f"An error occurred while trying to get the list")
        print(f"Error: {e}")
bot.run('your_token')
