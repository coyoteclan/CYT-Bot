import discord
from discord.ext import commands
import requests
import asyncio
from random import randint

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(description="A random joke.")
    async def joke(self, ctx):
        try:
            jokeapi = "https://v2.jokeapi.dev/joke/Any"
            async with ctx.channel.typing():
                cycle = True
                while cycle:
                    response = requests.get(jokeapi)
                    data = response.json()
                    
                    safety = bool(data.get("safe", ""))
                    if safety:
                        cycle = False
                jtype = data.get("type")
                if jtype == "single":
                    await asyncio.sleep(1)
                    await ctx.send(data.get("joke"))
                elif jtype == "twopart":
                    if randint(0, 4) < 2:
                        await ctx.send("hold up")
                    else:
                        await ctx.send("one joke coming right up")
                    async with ctx.channel.typing():
                        await asyncio.sleep(1)
                        await ctx.send(data.get("setup"))
                        async with ctx.channel.typing():
                            await asyncio.sleep(2)
                            await ctx.send(data.get("delivery"))
        except Exception as e:
            print(e)
    
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(description="Roast a friend.")
    async def roast(self, ctx, member:discord.Member):
        try:
            url = "https://ai4free-vortex-3b-roast-api.hf.space/generate-roasts/"
            payload = {
                "content": f"Roast my friend {member.display_name}. Keep it clean though."
            }
            async with ctx.channel.typing():
                response = requests.post(url, json=payload)
                roasts = response.json().get("roasts")
                if not roasts:
                    await ctx.reply("I can't think of anything to roast them with.")
                    return
                roast = roasts[randint(0, len(roasts)-1)]
                await ctx.send(f"||{member.mention}||, {roast}")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Fun(bot))
