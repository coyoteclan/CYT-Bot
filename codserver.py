import shared
#from shared import loadedServers

import discord
from discord.ext import commands
from discord.ui import Select, View, Button

class CoDServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description="Get status of a server.")
    async def status(self, ctx, server:str) -> None:
        guild_id = str(ctx.guild.id)
        try:
            shared.loadServers(guild_id)
            servers = shared.loadedServers[guild_id].keys()
            if server not in servers:
                await ctx.reply("Server not found.")
                return
        except Exception as e:
            print(e)
        
        async with ctx.typing():
            try:
                ip = shared.loadedServers[guild_id][server].get("ip")
                port = int(shared.loadedServers[guild_id][server].get("port"))
                server_url = f"https://cod.pm/server/{ip}/{port}"
                svInfo = await shared.getSVInfo(ip, port)

                embed = discord.Embed(title="Server Status", color=shared.embedColor)
                embed.add_field(name="Server Name", value=f"[{svInfo[0]}]({server_url})", inline=True)
                embed.add_field(name="Map", value=svInfo[1], inline=True)
                embed.add_field(name="Gametype", value=svInfo[2], inline=True)
                embed.add_field(name="Location", value=svInfo[3], inline=True)
                embed.set_image(url=svInfo[4])
                embed.add_field(name="Players", value=svInfo[5], inline=True)

                if svInfo[6]:
                    for page, table in svInfo[6].items():
                        embed.add_field(name=page, value=table, inline=False)
                
                view = View()
                if svInfo[0] != "N/A":
                    redirUrl = f"https://coyoteclan.github.io/iw1x-redirect/?ip={ip}&port={port}"
                    joinButton = Button(style=discord.ButtonStyle.blurple, label="Join Server", url=redirUrl)
                    view.add_item(item=joinButton)
                else:
                    embed.color = shared.errColor

                await ctx.reply(embed=embed, view=view)
            except discord.Forbidden:
                await ctx.reply("I do not have the permission to send embeds.")
            except Exception as e:
                print(f"Error in status function: {e}")
    
    @commands.command(description="Get a list of saved servers.") 
    async def servers(self, ctx) -> None:
        guild_id = str(ctx.guild.id)
        try:
            async with ctx.typing():
                shared.loadServers(guild_id)
                servers:dict = shared.loadedServers[guild_id]
                if servers and len(servers) != 0:
                    list = "\n".join([f"- {name}" for name in servers.keys()])
                    await ctx.reply(f"{shared.BU('Saved Servers')}:\n {list}")
                    return
                await ctx.reply("No saved servers... yet. Try ``addserver`` cmd.")
        except Exception as e:
            print(f"{e}")
    
    @commands.command(description="Save a new server. If server exists, will be overwritten.", aliases=['savesv', 'saveserver', 'newsv', 'newserver'])
    async def addserver(self, ctx, name:str, ip:str, _port:str) -> None:
        guild_id = str(ctx.guild.id)
        port = int(_port)
        async with ctx.typing():
            shared.loadedServers[guild_id][name] = {"ip": ip, "port": port}
            shared.saveServers(guild_id)
            await ctx.reply(f"{shared.BU('Added server')}: {name} ({ip}:{port})")
    
    @commands.command(description="Delete a server.", aliases=['delsv', 'rmsv', 'removesv'])
    async def removeserver(self, ctx, name:str) -> None:
        guild_id = str(ctx.guild.id)
        async with ctx.typing():
            try:
                if name not in shared.loadedServers[guild_id]:
                    await ctx.reply(f"{shared.BU('Error')}: Server `{name}` not found.")
                    return
                
                shared.loadedServers[guild_id].pop(name)
                shared.saveServers(guild_id)
                await ctx.reply(f"{shared.BU('Removed server')}: {name}")

            except KeyError:
                await ctx.reply(f"{shared.BU('Error')}: No servers found for this guild.")

            except Exception as e:
                print(f"Error in removeserver: {e}")
    
    @commands.command(description="afjajoa")
    async def masterlist(self, ctx, game:str, version:str) -> None:
        try:
            async with ctx.typing():
                embed, view = shared.ms_embed(game, version)
                await ctx.reply(embed=embed, view=view)
        except Exception as e:
            print(f"Error in masterlist: {e}")

async def setup(bot):
    await bot.add_cog(CoDServer(bot))
