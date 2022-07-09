import os
import nextcord
from nextcord.ext import commands
from config import settings
from webserver import keep_alive

token = os.environ['token']

client = commands.Bot(command_prefix=settings['PREFIX'], case_insensitive=True, intents=nextcord.Intents.all())
client.remove_command('help')

if __name__ == '__main__':
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            client.load_extension(f'commands.{filename[: -3]}')
            print(f'commands.{filename[: -3]} загружен')
    client.run(token, reconnect=True)
