# CYT-COD-Server-Utility
Our tool for some cod server related tasks

## Features
- Bans list and details for each ban
- Reports list and details for each report
- Clear Reports
- Get Server status
- Ban a player from discord
- Unban a player from discord
- Added the function to remove color tags from player name
- Bot now watches the reports file for new reports (Local version)
- Added Banlog (Local Version)

## Changes
- Organized the code

## Requirements
- Python 3.8.10 or later would be good but python 3.7 also works
- ### Modules:
- discord
- asyncio
- requests
- paramiko (for sftp version)
## Usage
- Use local version if server is on local machine.
- Use sftp verion if you use sftp to access server files
- Fill up the required fields
- Add your bot's token in the last line
- For Windows:
Run bot.py with C:/Windows/py.exe
- For Linux:
Type `cd <bot directory>` and then `python3 bot.py` in terminal

For further help, feel free to contact on <a href="https://discord.com/users/932181218936651827">Discord</a>
