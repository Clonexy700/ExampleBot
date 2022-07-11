import nextcord
from nextcord.ext import commands
import random
from config import settings


class EventsListener(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=nextcord.Game(name=f"{random.choice(settings['presences'])}\n"
                                                                      f"{settings['PREFIX']}help"))

    @commands.Cog.listener()
    async def on_message(self, message):
        message_content = message.content.casefold()
        ban_links = ["discord.gg", ".gg"]
        for link in ban_links:
            if link in message_content:
                await message.delete()


def setup(client):
    client.add_cog(EventsListener(client))
