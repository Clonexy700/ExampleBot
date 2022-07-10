import nextcord
from nextcord.ext import commands
from nextcord.utils import get
import sqlite3
import locale
from datetime import datetime
from config import settings


class MarriageListener(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS marriage (
            user_id INTERGER, pair_id INTERGER, date TEXT
        )""")
        db.commit()

        for guild in self.client.guilds:
            for member in guild.members:
                if not member.bot:
                    if cursor.execute(f"SELECT user_id FROM marriage WHERE user_id = {member.id}").fetchone() is None:
                        sql = "INSERT INTO marriage(user_id, pair_id, date) VALUES (?, ?, ?)"
                        val = (member.id, 0, '0')
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
        cursor.execute(f"SELECT user_id FROM marriage WHERE user_id = {author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO marriage(user_id, pair_id, date) VALUES (?, ?, ?)"
            val = (message.author.id, 0, '0')
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if not member.bot:
            if cursor.execute(f"SELECT user_id FROM marriage WHERE user_id = {member.id}").fetchone() is None:
                sql = "INSERT INTO marriage(user_id, pair_id, date) VALUES (?, ?, ?)"
                val = (member.id, 0, '0')
                cursor.execute(sql, val)
                db.commit()
        cursor.close()
        db.close()

    @commands.command(aliases=['marry', 'свадьба'])
    async def __marry(self, ctx, user: nextcord.Member = None):
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}marry <пользователь>')
            return await ctx.send(embed=embed)
        if user.bot:
            return await ctx.send('Нельзя указывать бота!!!')
        if user == ctx.author:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Нельзя устроить свадьбу с самим собой')
            return await ctx.send(embed=embed)
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT pair_id FROM marriage WHERE user_id = {ctx.author.id}")
        partner = cursor.fetchone()
        try:
            partner = partner[0]
        except:
            return await ctx.send('что-то с бд!!!')
        if partner != 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Вы уже женаты.')
            return await ctx.send(embed=embed)
        cursor.execute(f"SELECT pair_id FROM marriage WHERE user_id = {user.id}")
        partner = cursor.fetchone()
        try:
            partner = partner[0]
        except:
            return await ctx.send('что-то с бд!!!')
        if partner != 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Данный пользователь уже женат.')
            return await ctx.send(embed=embed)
        cursor.execute(f"SELECT user_id FROM marriage WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO marriage(user_id, pair_id, date) VALUES (?, ?, ?)"
            val = (ctx.author.id, 0, '0')
            cursor.execute(sql, val)
            db.commit()
        cursor.execute(f"SELECT user_id FROM marriage WHERE user_id = {user.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO marriage(user_id, pair_id, date) VALUES (?, ?, ?)"
            val = (user.id, 0, '0')
            cursor.execute(sql, val)
            db.commit()

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.add_field(name='Свадьба',
                             value=f'{ctx.author.mention} предлагает вам свою руку и сердце! {user.mention}',
                             inline=False)
        embed.add_field(name='Каков будет ваш ответ?',
                             value='Вы можете ответить с помощью **да** или **нет**, у вас есть целая минута, '
                                   'чтобы принять '
                                   'решение!',
                             inline=False)
        await ctx.send(embed=embed)

        def check(user):
            def inner_check(message):
                return message.author == user and \
                       (message.content.casefold() == "да" or message.content.casefold() == "нет")

            return inner_check

        reply = await self.client.wait_for('message', check=check(user), timeout=30)
        if reply.content.casefold() == 'нет':
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Свадьба неудачна',
                            value=f'Время истекло или пользователь отказался от предложения',
                            inline=False)
            await ctx.send(embed=embed)
        if reply.content.casefold() == 'да':
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Свадьба успешна',
                            value=f'{ctx.author.mention} и {user.mention} обвенчались.',
                            inline=False)
            await ctx.send(embed=embed)
            sql = "UPDATE marriage SET pair_id = ? WHERE user_id = ?"
            val = (user.id, ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            locale.setlocale(locale.LC_TIME, "ru_RU")
            date_format = "%a, %d %b %Y %H:%M:%S"
            timestamp = datetime.now()
            date = timestamp.strftime(date_format)
            sql = "UPDATE marriage SET date = ? WHERE user_id = ?"
            val = (date, ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            sql = "UPDATE marriage SET pair_id = ? WHERE user_id = ?"
            val = (ctx.author.id, user.id)
            cursor.execute(sql, val)
            db.commit()
            sql = "UPDATE marriage SET date = ? WHERE user_id = ?"
            val = (date, user.id)
            cursor.execute(sql, val)
            db.commit()
        cursor.close()
        db.close()

    @__marry.error
    async def marry_timeout(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Свадьба неудачна',
                            value=f'Время истекло или пользователь отказался от предложения',
                            inline=False)
            await ctx.send(embed=embed)

    @commands.command(aliases=['divorce', 'развод'])
    async def __divorce(self, ctx):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT pair_id FROM marriage WHERE user_id = {ctx.author.id}")
        partner = cursor.fetchone()
        try:
            partner = partner[0]
        except:
            return await ctx.send('что-то с бд!!!')
        if partner == 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'У вас уже нет или не было пары')
            return await ctx.send(embed=embed)
        sql = "UPDATE marriage SET pair_id = ? WHERE user_id = ?"
        val = (0, partner)
        cursor.execute(sql, val)
        db.commit()
        sql = "UPDATE marriage SET date = ? WHERE user_id = ?"
        val = ('0', partner)
        cursor.execute(sql, val)
        db.commit()
        sql = "UPDATE marriage SET pair_id = ? WHERE user_id = ?"
        val = (0, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        sql = "UPDATE marriage SET date = ? WHERE user_id = ?"
        val = ('0', ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        user = await self.client.fetch_user(partner)
        embed.add_field(name='Развод', value=f'{ctx.author.name} и {user.name} теперь разведены и больше не пара')
        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    @commands.command(aliases=['lprofile', 'lp', 'lovep', 'loveprofile'])
    async def __lprofile(self, ctx):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT pair_id FROM marriage WHERE user_id = {ctx.author.id}")
        partner = cursor.fetchone()
        try:
            partner = partner[0]
        except:
            return await ctx.send('что-то с бд!!!')
        if partner == 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'У вас нет пары')
            return await ctx.send(embed=embed)
        user = await self.client.fetch_user(partner)

        cursor.execute(f"SELECT date FROM marriage WHERE user_id = {ctx.author.id}")
        date = cursor.fetchone()
        try:
            date = date[0]
        except:
            return await ctx.send('что-то с бд!!!')
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_footer(text=f"IDs:\n{ctx.author.id}\n{user.id}", icon_url=user.avatar.url)
        embed.set_author(icon_url=ctx.author.avatar.url, name='Профиль пары')
        embed.add_field(name='_ _', value=f'{ctx.author.mention} :hearts: {user.mention}\n '
                                          f'Брак был заключен: `{date}`')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(MarriageListener(client))
