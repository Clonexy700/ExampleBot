import asyncio

import nextcord
from nextcord.ext import commands
from nextcord.utils import get
import sqlite3
import random
from config import settings


class LevelingSystem(commands.Cog):
    def __init__(self, client):
        self.client = client

    def lvl_up(self, author_id):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT lvl, exp FROM levels WHERE user_id = {author_id}")
        leveling = cursor.fetchone()
        try:
            current_lvl = leveling[0]
            current_exp = leveling[1]
        except:
            return print('что-то с бд!!!')

        if current_exp >= round((30 * (current_lvl ** 2))):

            sql = "UPDATE levels SET lvl = ? WHERE user_id = ?"
            val = (current_lvl + 1, author_id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            return True
        else:
            cursor.close()
            db.close()
            return False

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS levels (
            user_id INTERGER, lvl INTERGER, exp INTERGER
        )""")
        db.commit()

        for guild in self.client.guilds:
            for member in guild.members:
                if not member.bot:
                    if cursor.execute(f"SELECT user_id FROM levels WHERE user_id = {member.id}").fetchone() is None:
                        sql = "INSERT INTO levels(user_id, lvl, exp) VALUES (?, ?, ?)"
                        val = (member.id, 1, 0)
                        cursor.execute(sql, val)
                        db.commit()

        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.author == self.client.user:
            return
        if not message.guild:
            return
        author_id = message.author.id
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM levels WHERE user_id = {author_id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO levels(user_id, lvl, exp) VALUES (?, ?, ?)"
            val = (author_id, 1, 0)
            cursor.execute(sql, val)
            db.commit()

        if len(message.content) > 3:
            await asyncio.sleep(1)
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT exp FROM levels WHERE user_id = {message.author.id}")
            current_exp = cursor.fetchone()
            try:
                current_exp = current_exp[0]
            except:
                return await print('что-то с бд!!!')
            sql = "UPDATE levels SET exp = ? WHERE user_id = ?"
            val = (current_exp + random.randint(0, 2), author_id)
            cursor.execute(sql, val)
            db.commit()

        if self.lvl_up(author_id):
            embed = nextcord.Embed(color=settings['defaultBotColor'])
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
            cursor.execute(f"SELECT lvl FROM levels WHERE user_id = {author_id}")
            leveling = cursor.fetchone()
            try:
                current_lvl = leveling[0]
            except:
                print('БД ПИЗДЕЦ')
            embed.add_field(name='Повышение уровня',
                            value=f"{message.author.mention} достиг {current_lvl} уровня.")
            await message.channel.send(embed=embed)

        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if not member.bot:
            if cursor.execute(f"SELECT user_id FROM levels WHERE user_id = {member.id}").fetchone() is None:
                sql = "INSERT INTO levels(user_id, lvl, exp) VALUES (?, ?, ?)"
                val = (member.id, 1, 0)
                cursor.execute(sql, val)
                db.commit()
        cursor.close()
        db.close()

    @commands.command(aliases=['lvl', 'level', 'лвл', 'левел', 'уровень'])
    async def __level(self, ctx, user: nextcord.Member = None):
        user = ctx.author if not user else user

        if user.bot:
            return await ctx.send('Нельзя указывать бота!!!')

        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()

        if cursor.execute(f"SELECT user_id FROM levels WHERE user_id = {user.id}").fetchone() is None:
            sql = "INSERT INTO levels(user_id, lvl, exp) VALUES (?, ?, ?)"
            val = (user.id, 1, 0)
            cursor.execute(sql, val)
            db.commit()

        cursor.execute(f"SELECT lvl, exp FROM levels WHERE user_id = {user.id}")
        leveling = cursor.fetchone()
        try:
            level = leveling[0]
            exp = leveling[1]
        except:
            return await ctx.send('что-то с бд!!!')

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=user.name, icon_url=user.avatar.url)
        embed.add_field(name='Уровень', value=f'Ваш уровень: `{level}`\n Опыт: `{exp}/{round((30 * (level ** 2)))}`')
        embed.set_footer(text=random.choice(settings['footers']))

        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.command(aliases=['pleaderboard', 'ld', 'lld', 'top profiles',
                               'proftop', 'topprof', 'ptop', 'topp', 'ltop', 'topl', 'lleaderboard', 'лтоп', 'птоп'])
    async def __level_leaderboard(self, ctx):
        async with ctx.channel.typing():
            counter = 0
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            users = []
            for row in cursor.execute("SELECT user_id, lvl, exp FROM levels ORDER BY exp DESC LIMIT 15"):
                counter += 1
                user = await self.client.fetch_user(row[0])
                users.append(f'`#{counter}`. {user.mention}, `Уровень: {row[1]}, '
                             f'опыт: {row[2]}/{round((30 * (row[1] ** 2)))}`\n')
            description = ' '.join([user for user in users])
            embed = nextcord.Embed(title='Топ 15 сервера по уровням', color=settings['defaultBotColor'],
                                   timestamp=ctx.message.created_at, description=description)

            await ctx.send(embed=embed)

    @__level_leaderboard.error
    async def level_leaderboard_cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value='Команда сейчас недоступна, '
                                                 'попробуйте позже, через %.2fs секунд' % error.retry_after)
            await ctx.send(embed=embed)
        raise error


def setup(client):
    client.add_cog(LevelingSystem(client))
