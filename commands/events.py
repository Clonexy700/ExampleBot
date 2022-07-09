import nextcord
from nextcord.ext import commands
import os
import random
from config import settings


class EventsListener(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=nextcord.Game(name=f"{random.choice(settings['presences'])}\n"
                                                                      f"{settings['PREFIX']}help"))


def setup(client):
    client.add_cog(EventsListener(client))
