import nextcord
from nextcord.ext import commands
from nextcord.utils import get
import random
import sqlite3
from config import settings


class Economics(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS money (
            user_id INTERGER, money INTERGER
        )""")
        db.commit()

        for guild in self.client.guilds:
            for member in guild.members:
                if not member.bot:
                    if cursor.execute(f"SELECT user_id FROM money WHERE user_id = {member.id}").fetchone() is None:
                        sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
                        val = (member.id, 100)
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
        cursor.execute(f"SELECT user_id FROM money WHERE user_id = {author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
            val = (author.id, 100)
            cursor.execute(sql, val)
            db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if not member.bot:
            if cursor.execute(f"SELECT user_id FROM money WHERE user_id = {member.id}").fetchone() is None:
                sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
                val = (member.id, 100)
                cursor.execute(sql, val)
                db.commit()
        cursor.close()
        db.close()

    @commands.cooldown(1, 100, commands.BucketType.user)
    @commands.command(aliases=['moneydaily', 'ежедн', 'ежедневное', 'timely', 'еж', 'денежка', 'dailymoney',
                               'daily', 'награда', 'таймли', 'тайм', 'ежед', 'еже'])
    async def __daily(self, ctx):

        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance + 100, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.add_field(name='Денежное вознаграждение', value=f'Вы получили 100 валюта_нейм')
        embed.set_footer(text=random.choice(settings['footers']))

        await ctx.send(embed=embed)

    @__daily.error
    async def daily_cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value='Команда сейчас недоступна, '
                                                 'попробуйте позже, через %.2fs секунд' % error.retry_after)
            await ctx.send(embed=embed)
        raise error

    @commands.command(aliases=['bal', 'бал', 'баланс', 'money', 'balance', '$', 'wallet', 'мани', 'b', 'б'])
    async def __balance(self, ctx, user: nextcord.Member = None):
        user = ctx.author if not user else user

        if user.bot:
            return await ctx.send('Нельзя указывать бота!!!')

        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()

        if cursor.execute(f"SELECT user_id FROM money WHERE user_id = {user.id}").fetchone() is None:
            sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
            val = (user.id, 100)
            cursor.execute(sql, val)
            db.commit()

        cursor.execute(f"SELECT money FROM money WHERE user_id = {user.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=user.name, icon_url=user.avatar.url)
        embed.add_field(name='Баланс', value=f'У {user.name} на счету `{balance}` валюта_нейм')
        embed.set_footer(text=random.choice(settings['footers']))

        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.command(aliases=['give', 'transfer', 'дать', 'на', 'moneysend', 'sendmoney', 'send'])
    async def __transfer(self, ctx, user: nextcord.Member = None, amount: int = 0):
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}give <пользователь> <количество>')
            return await ctx.send(embed=embed)
        if user.bot:
            return await ctx.send('Нельзя указывать бота!!!')
        if amount <= 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите количество валюты: '
                                                 f'{settings["PREFIX"]}give <пользователь> <количество>')
            return await ctx.send(embed=embed)

        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()

        if cursor.execute(f"SELECT user_id FROM money WHERE user_id = {user.id}").fetchone() is None:
            sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
            val = (user.id, 100)
            cursor.execute(sql, val)
            db.commit()

        cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}")
        sender_balance = cursor.fetchone()
        try:
            sender_balance = sender_balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        if sender_balance < amount:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'У вас недостаточно валюта_нейм для отправки')
            return await ctx.send(embed=embed)

        cursor.execute(f"SELECT money FROM money WHERE user_id = {user.id}")
        recipient_balance = cursor.fetchone()
        try:
            recipient_balance = recipient_balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (sender_balance - amount, ctx.author.id)
        cursor.execute(sql, val)

        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (recipient_balance + amount, user.id)
        cursor.execute(sql, val)

        db.commit()

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.add_field(name='Передача валюты', value=f'{ctx.author.name} передал {user.name} {amount} валюта_нейм')
        embed.set_footer(text=f'транзакция №{random.randint(1, 1000000000)}', icon_url=user.avatar)

        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.command(aliases=['mleaderboard', 'mld', 'topmoney', 'mtop', 'topm', 'мтоп'])
    async def __money_leaderboard(self, ctx):
        async with ctx.channel.typing():
            counter = 0
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            users = []
            for row in cursor.execute("SELECT user_id, money FROM money ORDER BY money DESC LIMIT 15"):
                counter += 1
                user = await self.client.fetch_user(row[0])
                users.append(f'`#{counter}`. {user.mention}, `Баланс: {row[1]}`\n')
            description = ' '.join([user for user in users])
            embed = nextcord.Embed(title='Топ 15 сервера по валюте', color=settings['defaultBotColor'],
                                   timestamp=ctx.message.created_at, description=description)

            await ctx.send(embed=embed)

    @__money_leaderboard.error
    async def level_leaderboard_cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value='Команда сейчас недоступна, '
                                                 'попробуйте позже, через %.2fs секунд' % error.retry_after)
            await ctx.send(embed=embed)
        raise error


def setup(client):
    client.add_cog(Economics(client))
