import nextcord
from nextcord.ext import commands, tasks
import os
import random
from config import settings


class LoopHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.task_loop.start()

    @tasks.loop(seconds=60)
    async def task_loop(self):
        guild = self.client.get_guild(settings['guild_id'])
        voice_members = set()
        for voice_channel in guild.voice_channels:
            for member in voice_channel.members:
                voice_members.add(member.id)
        channel = self.client.get_channel(settings['active_voice_member_count_channel'])
        voice_members_counter = len(voice_members)
        await channel.edit(name=f"PSYCHO: voice {voice_members_counter}")


def setup(client):
    client.add_cog(LoopHandler(client))