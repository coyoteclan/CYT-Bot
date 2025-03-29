# CYT-COD-Server-Utility
Our tool for some cod server related tasks
> **Note:**
>
> The bot is being re-written. Some features have been dropped and some are not added yet.

## Features
- Get Server status
- Function to remove color tags from player name
- Ability to add servers through command
- Remove servers using command
- Can retrieve cod, coduo, cod2 and cod4 masterlist from [cod.pm api](https://api.cod.pm)

## Requirements
- Python 3.11.2 or later recommended
- ### Modules:
- discord
- asyncio
- requests
- tabulate
- cython
- ~~paramiko (for sftp version)~~
## Usage
- Set bot token in ``config.json``
- Create a folder named ``servers`` with ``bot.py``
For Windows:
- Run ``bot.py`` with C:/Windows/py.exe
For Linux:
- Delete ``shared.py`` file
- Type ``python3 bot.py`` in terminal

For further help, feel free to contact on <a href="https://discord.com/users/932181218936651827">Discord</a>
