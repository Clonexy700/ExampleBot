import nextcord
from nextcord.ext import commands
import sqlite3
import random
import datetime
import humanfriendly
from datetime import timedelta
import asyncio
import re
import locale
from config import settings


def format_seconds_to_hhmmss(seconds):
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)


class VoiceHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS voice (
            user_id INTERGER, time TEXT, leave_time TEXT, join_time TEXT)""")
        db.commit()

        for guild in self.client.guilds:
            for member in guild.members:
                if not member.bot:
                    if cursor.execute(f"SELECT user_id FROM voice WHERE user_id = {member.id}").fetchone() is None:
                        sql = "INSERT INTO voice(user_id, time, leave_time, join_time) VALUES (?, ?, ?, ?)"
                        val = (member.id, '0', '0', '0')
                        cursor.execute(sql, val)
                        db.commit()

        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if not member.bot:
            if cursor.execute(f"SELECT user_id FROM voice WHERE user_id = {member.id}").fetchone() is None:
                sql = "INSERT INTO voice(user_id, time, leave_time, join_time) VALUES (?, ?, ?, ?)"
                val = (member.id, '0', '0', '0')
                cursor.execute(sql, val)
                db.commit()
        new_user = member.id
        query = cursor.execute(f"SELECT join_time FROM voice WHERE user_id = {member.id}").fetchone()[0]
        if query != '0':
            if before.channel is not None and after.channel is None:

                voice_leave_time = datetime.datetime.now().time().strftime('%H:%M:%S')
                voice_join_time = query

                calculate_time = abs(
                    datetime.datetime.strptime(voice_leave_time, '%H:%M:%S') - datetime.datetime.strptime(
                        voice_join_time, '%H:%M:%S'))

                minutes_in_voice = abs(int(
                    calculate_time.total_seconds() / 60))  # считаем минуты в войсе чтобы начислить валюту и опыт

                second_in_voice = abs(calculate_time.total_seconds())

                timing = cursor.execute(f"SELECT time FROM voice WHERE user_id = {member.id}").fetchone()[0]

                if timing == '0':
                    add_time = second_in_voice
                else:
                    add_time = float(timing) + second_in_voice
                sql = "UPDATE voice SET time = ? WHERE user_id = ?"
                print(format_seconds_to_hhmmss(float(add_time)))
                val = (str(add_time), new_user)
                cursor.execute(sql, val)
                db.commit()

                sql = "UPDATE voice SET join_time = ? WHERE user_id = ?"
                val = ('0', new_user)
                cursor.execute(sql, val)
                db.commit()

                cursor.execute(f"SELECT user_id FROM levels WHERE user_id = {new_user}")

                result = cursor.fetchone()
                if result is None:
                    sql = "INSERT INTO levels(user_id, lvl, exp) VALUES (?, ?, ?)"
                    val = (new_user, 1, 0)
                    cursor.execute(sql, val)
                    db.commit()

                cursor.execute(f"SELECT exp FROM levels WHERE user_id = {new_user}")
                current_exp = cursor.fetchone()
                try:
                    current_exp = current_exp[0]
                except:
                    return await print('что-то с бд!!!')

                sql = "UPDATE levels SET exp = ? WHERE user_id = ?"
                val = (abs(current_exp + int(random.randint(1, 2) * minutes_in_voice)), new_user)
                cursor.execute(sql, val)
                db.commit()

                cursor.execute(f"SELECT user_id FROM money WHERE user_id = {new_user}")
                result = cursor.fetchone()
                if result is None:
                    sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
                    val = (new_user, 100)
                    cursor.execute(sql, val)
                    db.commit()

                cursor.execute(f"SELECT money FROM money WHERE user_id = {new_user}")
                balance = cursor.fetchone()
                try:
                    balance = balance[0]
                except:
                    return await print('что-то с бд!!!')

                sql = "UPDATE money SET money = ? WHERE user_id = ?"
                val = ((abs(balance + int(6) * minutes_in_voice)), new_user)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()

        else:
            if before.channel is None and after.channel is not None:
                new_voice_join_time = datetime.datetime.now().time().strftime('%H:%M:%S')
                sql = "UPDATE voice SET join_time = ? WHERE user_id = ?"
                val = (new_voice_join_time, new_user)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if not member.bot:
            if cursor.execute(f"SELECT user_id FROM voice WHERE user_id = {member.id}").fetchone() is None:
                sql = "INSERT INTO voice(user_id, time, leave_time, join_time) VALUES (?, ?, ?, ?)"
                val = (member.id, '0', '0', '0')
                cursor.execute(sql, val)
                db.commit()
        cursor.close()
        db.close()

    @commands.command(aliases=['voiceonline', 'онлайн', 'вонлайн', 'vonline', 'online'])
    async def __vonline(self, ctx, user: nextcord.Member = None):
        if user is None:
            user = ctx.author
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        user_time = cursor.execute(f"SELECT time FROM voice WHERE user_id = {user.id}").fetchone()[0]
        user_time = format_seconds_to_hhmmss(float(user_time))
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=user.name, icon_url=user.avatar)
        voice_members = set()
        for voice_channel in ctx.guild.voice_channels:
            for member in voice_channel.members:
                voice_members.add(member.id)
        number_of_people_in_voice = len(voice_members)
        embed.add_field(name='Время пользователя в голосовых каналах', value=f'Вы провели `{user_time}` времени'
                                                                             f' в голосовых чатах сервера!\n '
                                                                             f'В голосовых чатах сервера сейчас всего:'
                                                                             f'`{number_of_people_in_voice}`'
                                                                             f'пользователей')
        embed.set_footer(text=random.choice(settings['footers']))

        await ctx.send(embed=embed)

        channel = self.client.get_channel(settings['active_voice_member_count_channel'])
        await channel.edit(name=f"PSYCHO: voice {number_of_people_in_voice}")

    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.command(aliases=['vleaderboard', 'vld', 'vlld', 'vtop', 'voicetop', 'topv', 'toppv', 'voicetoplead',
                               'topvo', 'voiceleaderboard', 'войстоп', 'втоп', 'топв'])
    async def __voice_leaderboard(self, ctx):
        async with ctx.channel.typing():
            counter = 0
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            users = []
            for row in cursor.execute("SELECT user_id, time FROM voice ORDER BY strftime('%s', time) ASC LIMIT 15"):
                counter += 1
                user = await self.client.fetch_user(row[0])
                users.append(f'`#{counter}`. {user.mention}, `Время: {format_seconds_to_hhmmss(float(row[1]))}\n`')
            description = ' '.join([user for user in users])
            embed = nextcord.Embed(title='Топ 15 сервера по времени в голосовых каналах',
                                   color=settings['defaultBotColor'],
                                   timestamp=ctx.message.created_at, description=description)

            await ctx.send(embed=embed)

    @__voice_leaderboard
    async def __voice__leaderboard__cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value='Команда сейчас недоступна, '
                                                 'попробуйте позже, через %.2fs секунд' % error.retry_after)
            await ctx.send(embed=embed)
        raise error


def setup(client):
    client.add_cog(VoiceHandler(client))
