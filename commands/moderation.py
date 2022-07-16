import nextcord
from nextcord.ext import commands
import sqlite3
import random
import datetime
import humanfriendly
import asyncio
import locale
from config import settings


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS warns (
            user_id INTERGER, warns INTERGER, date_1 TEXT, reason_1 TEXT, 
            date_2 TEXT, reason_2 TEXT, date_3 TEXT, reason_3 TEXT
        )""")
        db.commit()

        for guild in self.client.guilds:
            for member in guild.members:
                if not member.bot:
                    if cursor.execute(f"SELECT user_id FROM warns WHERE user_id = {member.id}").fetchone() is None:
                        sql = "INSERT INTO warns(user_id, warns, date_1, reason_1, date_2, reason_2, date_3, " \
                              "reason_3) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                        val = (member.id, 0, '0', '0', '0', '0', '0', '0')
                        cursor.execute(sql, val)
                        db.commit()

        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        author = message.author
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM warns WHERE user_id = {author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO warns(user_id, warns, date_1, reason_1, date_2, reason_2, date_3, " \
                  "reason_3) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            val = (message.author.id, 0, '0', '0', '0', '0', '0', '0')
            cursor.execute(sql, val)
            db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if not member.bot:
            if cursor.execute(f"SELECT user_id FROM warns WHERE user_id = {member.id}").fetchone() is None:
                sql = "INSERT INTO warns(user_id, warns, date_1, reason_1, date_2, reason_2, date_3, " \
                      "reason_3) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                val = (member.id, 0, '0', '0', '0', '0', '0', '0')
                cursor.execute(sql, val)
                db.commit()
        cursor.close()
        db.close()

    @commands.command(aliases=['mute', 'timeout', 'm', 'мут'])
    @commands.has_permissions(manage_messages=True)
    async def __mute(self, ctx, user: nextcord.Member = None, time: str = None, *, reason: str = 'не указана'):
        try:
            if user is None:
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'Правильное написание команды: \n'
                                                     f'{settings["PREFIX"]}mute <пользователь> <время в формате: 1d/1h/1m/1s> <причина>')
                return await ctx.send(embed=embed)
            if time is None:
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'Правильное написание команды: \n'
                                                     f'{settings["PREFIX"]}mute <пользователь> <время в формате: 1d 1h 1m 1s> <причина>')
                return await ctx.send(embed=embed)
            if user == ctx.author:
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'Нельзя замутить самого себя')
                return await ctx.send(embed=embed)
            time_in_seconds = humanfriendly.parse_timespan(time)
            if time_in_seconds > 1296000.0:
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'Слишком большое время мута, может забаним его?')
                return await ctx.send(embed=embed)
            await user.edit(timeout=nextcord.utils.utcnow() + datetime.timedelta(seconds=time_in_seconds))
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Мут',
                            value=f'{ctx.author.mention} выдал мут {user.mention}\nПричина мута: `{reason}`\n'
                                  f'Время мута: {time} ')
            await ctx.send(embed=embed)
        except nextcord.Forbidden:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка',
                            value=f'Этого пользователя нельзя замутить, или у меня недостаточно прав')
            await ctx.send(embed=embed)

    @commands.command(aliases=['unmute', 'um', 'размут'])
    @commands.has_permissions(manage_messages=True)
    async def __unmute(self, ctx, user: nextcord.Member):
        await user.edit(timeout=None)
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.add_field(name='Отмена мута', value=f'{ctx.author.mention} размутил {user.mention}')
        return await ctx.send(embed=embed)

    @commands.command(aliases=['warn', 'w', 'варн', 'пред', 'предупреждение'])
    @commands.has_permissions(manage_messages=True)
    async def __warn(self, ctx, user: nextcord.Member = None, time: str = None, *, reason: str = 'не указана'):
        if time is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите время: \n'
                                                 f'{settings["PREFIX"]}warn <пользователь> <время в формате: 1d/1h/1m/1s> <причина>')
            return await ctx.send(embed=embed)
        if reason is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите причину, правильное написание: \n'
                                                 f'{settings["PREFIX"]}warn <пользователь> <время в формате: 1d/1h/1m/1s> <причина>')
            return await ctx.send(embed=embed)
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите пользователя, правильное написание: \n'
                                                 f'{settings["PREFIX"]}warn <пользователь> <время в формате: 1d/1h/1m/1s> <причина>')
            return await ctx.send(embed=embed)
        if user == ctx.author:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Нельзя выдать варн самому себе')
            return await ctx.send(embed=embed)
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.add_field(name='Предупреждение',
                        value=f'{ctx.author.mention} выдал варн {user.mention}\nПричина: `{reason}`')
        embed.set_footer(text=f'warn ticket #{random.randint(1, 1000000000)}')
        await ctx.send(embed=embed)
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        time_in_seconds = humanfriendly.parse_timespan(time)
        warn_count = cursor.execute(f"SELECT warns FROM warns WHERE user_id = {user.id}").fetchone()[0]
        if warn_count == 0:
            warn_count += 1
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            date_format = "%a, %d %b %Y %H:%M:%S"
            timestamp = datetime.datetime.now()
            date = timestamp.strftime(date_format)
            sql = f"UPDATE warns SET date_{warn_count} = ? WHERE user_id = ?"
            val = (date, user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_{warn_count} = ? WHERE user_id = ?"
            val = (reason, user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (warn_count, user.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await asyncio.sleep(time_in_seconds)
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            sql = f"UPDATE warns SET date_{warn_count} = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_{warn_count} = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (warn_count-1, user.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        elif warn_count == 1:
            warn_count += 1
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            date_format = "%a, %d %b %Y %H:%M:%S"
            timestamp = datetime.datetime.now()
            date = timestamp.strftime(date_format)
            sql = f"UPDATE warns SET date_{warn_count} = ? WHERE user_id = ?"
            val = (date, user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_{warn_count} = ? WHERE user_id = ?"
            val = (reason, user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (warn_count, user.id)
            cursor.execute(sql, val)
            db.commit()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Мут по предупреждениям',
                            value=f'У {user.mention} 2 предупреждения, выдан автоматический мут на 1 час, ')
            await ctx.send(embed=embed)
            await user.edit(timeout=nextcord.utils.utcnow() + datetime.timedelta(seconds=3600))
            cursor.close()
            db.close()
            await asyncio.sleep(time_in_seconds)
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            locale.setlocale(locale.LC_TIME, "ru_RU")
            sql = f"UPDATE warns SET date_{warn_count} = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_{warn_count} = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (warn_count-1, user.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        elif warn_count == 2:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Мут по предупреждениям',
                            value=f'У {user.mention} 3 предупреждения, выдан автоматический мут на 12 часов, '
                                  f'предупреждения сняты')
            await ctx.send(embed=embed)
            await user.edit(timeout=nextcord.utils.utcnow() + datetime.timedelta(seconds=43200))
            sql = f"UPDATE warns SET reason_1 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_2 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET date_1 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET date_2 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (0, user.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @commands.command(aliases=['fullunwarn', 'fulluw', 'fuw', 'снятьпреды'])
    @commands.has_permissions(administrator=True)
    async def __unwarn_all(self, ctx, user: nextcord.Member = None):
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите пользователя, правильное написание: \n'
                                                 f'{settings["PREFIX"]}unwarn <пользователь>')
            return await ctx.send(embed=embed)
        if user == ctx.author:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Нельзя снять варн самому себе')
            return await ctx.send(embed=embed)
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        warn_count = cursor.execute(f"SELECT warns FROM warns WHERE user_id = {user.id}").fetchone()[0]
        if warn_count == 0:
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Снятие варна', value=f'У пользователя {user.mention} __**0**__ варнов')
            return await ctx.send(embed=embed)
        elif warn_count > 0:
            sql = f"UPDATE warns SET date_1 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_1 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (0, user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET date_2 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_2 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET date_3 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_3 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Снятие варна', value=f'Были сняты все варны \nУ пользователя {user.mention} теперь __**0**__ варнов')
            return await ctx.send(embed=embed)

    @commands.command(aliases=['unwarn', 'uw', 'анварн', 'снятьпред'])
    @commands.has_permissions(administrator=True)
    async def __unwarn(self, ctx, user: nextcord.Member = None):
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите пользователя, правильное написание: \n'
                                                 f'{settings["PREFIX"]}unwarn <пользователь>')
            return await ctx.send(embed=embed)
        if user == ctx.author:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Нельзя снять варн самому себе')
            return await ctx.send(embed=embed)
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        warn_count = cursor.execute(f"SELECT warns FROM warns WHERE user_id = {user.id}").fetchone()[0]
        if warn_count == 0:
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Снятие варна', value=f'У пользователя {user.mention} __**0**__ варнов')
            return await ctx.send(embed=embed)
        elif warn_count == 1:
            sql = f"UPDATE warns SET date_1 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_1 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (0, user.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Снятие варна', value=f'Был снят варн \nУ пользователя {user.mention} теперь __**0**__ варнов')
            return await ctx.send(embed=embed)
        elif warn_count == 2:
            sql = f"UPDATE warns SET date_2 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET reason_2 = ? WHERE user_id = ?"
            val = ('0', user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
            val = (1, user.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Снятие варна', value=f'Был снят варн \nУ пользователя {user.mention} теперь __**1**__ варн')
            return await ctx.send(embed=embed)

    @commands.command(aliases=['warns', 'view', 'варны', 'преды'])
    async def __warns(self, ctx, user: nextcord.Member = None):
        if user is None:
            user = ctx.author
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        warn_count = cursor.execute(f"SELECT warns FROM warns WHERE user_id = {user.id}").fetchone()[0]
        if warn_count == 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Список предупреждений',
                            value=f'У {user.mention} 0 предупреждений.')
            await ctx.send(embed=embed)
        if warn_count > 0:
            date_1 = cursor.execute(f"SELECT date_1 FROM warns WHERE user_id = {user.id}").fetchone()[0]
            date_2 = cursor.execute(f"SELECT date_1 FROM warns WHERE user_id = {user.id}").fetchone()[0]
            date_3 = cursor.execute(f"SELECT date_1 FROM warns WHERE user_id = {user.id}").fetchone()[0]
            reason_1 = cursor.execute(f"SELECT date_1 FROM warns WHERE user_id = {user.id}").fetchone()[0]
            reason_2 = cursor.execute(f"SELECT date_1 FROM warns WHERE user_id = {user.id}").fetchone()[0]
            reason_3 = cursor.execute(f"SELECT date_1 FROM warns WHERE user_id = {user.id}").fetchone()[0]
            if date_1 == '0' and date_2 == '0' and date_3 == '0' and reason_1 == '0' and reason_2 == '0' and reason_3 == '0':
                sql = f"UPDATE warns SET warns = ? WHERE user_id = ?"
                val = (0, user.id)
                cursor.execute(sql, val)
                db.commit()
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Список предупреждений',
                                value=f'У {user.mention} 0 предупреждений.')
                await ctx.send(embed=embed)
            else:
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Список предупреждений',
                                value=f'У {user.mention} {warn_count} предупреждений.', inline=False)
                for i in range(warn_count):
                    date_of_warn = \
                    cursor.execute(f"SELECT date_{i + 1} FROM warns WHERE user_id = {user.id}").fetchone()[0]
                    warn_reason = \
                    cursor.execute(f"SELECT reason_{i + 1} FROM warns WHERE user_id = {user.id}").fetchone()[
                        0]
                    embed.add_field(name=f'Варн #{i + 1}',
                                    value=f'Был получен: `{date_of_warn}`\nпо причине: `{warn_reason}`', inline=False)
                await ctx.send(embed=embed)
        cursor.close()
        db.close()


def setup(client):
    client.add_cog(Moderation(client))
