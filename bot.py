import shared
from shared import green, blue, yellow
from shared import lbreak
import discord
from discord.ext import commands
import asyncio

token = shared.config.get("token")
prefix = shared.config.get("prefix")

class MyClient(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {client.user} (ID: {client.user.id})")
        print(lbreak)

        for guild in self.guilds:
            guild_id = str(guild.id)
            shared.loadedServers[guild_id] = {}
            shared.loadServers(guild_id)
            print(f"Loaded servers for guild {guild.name}: {shared.loadedServers[guild_id]}")
    
    async def load_extensions(self):
        try:
            await self.load_extension('codserver')
            await self.load_extension('fun')
        except Exception as e:
            print(f'Failed to load extension: {e}')


intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
client = MyClient(command_prefix=prefix, activity=discord.Activity(type=discord.ActivityType.listening, name='+help'), intents=intents)

def run():
    asyncio.get_event_loop().run_until_complete(client.load_extensions())
    client.run(token)

if __name__ == "__main__":
    print(f"Bot made by {green('kazam0180')}{yellow('@')}{blue('discord')}.")
    asyncio.run(run())
