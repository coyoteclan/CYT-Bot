import asyncio
import os
import re
from datetime import datetime
import discord
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='zzzz', activity=discord.Activity(type=discord.ActivityType.watching, name="chat messages"), intents=intents)

chatlog = 1165118146345185330

async def send_to_cod(sender, message):
    print(f"{sender} says {message}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    print(message.channel.id)
    if message.channel.id == chatlog:
    	await send_to_cod(message.author, message.content)

bot.run('MTIwMDkwOTMyMjM4NTg4MzIxNw.GIR6ge.4nkCP5iE5fwYqtLBaSE4zUVotFi92jDlubLbqw')

class LogFileHandler(PatternMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_position = 0

    def on_modified(self, event):
        with open(event.src_path, "r") as log_file:
            log_file.seek(self.last_position)
            new_lines = log_file.readlines()

            for line in new_lines:
                if line.startswith("Joined"):
                    message = line.split(":", 1)[1].strip()
                    message = re.sub("@everyone|@here", "", message)
                    message = f"{message} joined the server!"
                    print(message)
                if line.startswith("Quit"):
                    message = line.split(":", 1)[1].strip()
                    message = re.sub("@everyone|@here", "", message)
                    message = f"{message} left the server :("
                    print(message)

            self.last_position = log_file.tell()

async def main():
    log_file_path = "test.log"
    new_log_file_path = f"test_{datetime.now()}.log"
    patterns = ["*.log"]

    if os.path.exists(log_file_path):
        os.rename(log_file_path, new_log_file_path)

    with open(log_file_path, "w"):
        pass

    event_handler = LogFileHandler(patterns=patterns)
    observer = Observer()
    observer.schedule(event_handler, path=log_file_path, recursive=False)
    observer.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    asyncio.run(main())