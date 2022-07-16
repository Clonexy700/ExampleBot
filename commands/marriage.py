import nextcord
from nextcord.ext import commands
import sqlite3
import locale
import asyncio
from nextcord.utils import get
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
    async def __marry(self, ctx, member: nextcord.Member = None):
        await ctx.send('ВНИМАНИЕ СЕЙЧАС ЗАПУЩЕНА ВЕРСИЯ БОТА ДЛЯ РАЗРАБОТКИ ВАШИ ДАННЫЕ НЕ БУДУТ СОХРАНЕНЫ')
        emoji = "<a:emoji_1:995590858734841938>"
        if member is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}marry <пользователь>')
            return await ctx.send(embed=embed)
        if member.bot:
            return await ctx.send('Нельзя указывать бота!!!')
        if member == ctx.author:
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
        cursor.execute(f"SELECT pair_id FROM marriage WHERE user_id = {member.id}")
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
        cursor.execute(f"SELECT user_id FROM marriage WHERE user_id = {member.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO marriage(user_id, pair_id, date) VALUES (?, ?, ?)"
            val = (member.id, 0, '0')
            cursor.execute(sql, val)
            db.commit()
        cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        if balance < 2000:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji}. Свадьба стоит 2000 {emoji}')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        emoji_marry = self.client.get_emoji(995605076108382288)
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.add_field(name=f'{emoji_marry} Свадьба',
                        value=f'{ctx.author.mention} предлагает вам свою руку и сердце! {member.mention}',
                        inline=False)
        embed.add_field(name='Каков будет ваш ответ?',
                        value='У вас есть целая минута, '
                              'чтобы принять '
                              'решение!\n С предложившего устроить свадьбу будет списано 2000 {emoji} при согласии',
                        inline=False)
        emoji_no = get(self.client.emojis, name='emoji_no')
        emoji_yes = get(self.client.emojis, name='emoji_yes')
        msg = await ctx.send(embed=embed)

        def check(reaction, user):
            return (reaction.message.id == msg.id) and (user == member)

        await msg.add_reaction(emoji_yes)
        await msg.add_reaction(emoji_no)
        print(emoji_yes.id)
        print(emoji_no.id)

        try:
            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            return
        print(str(reaction))
        print(str(emoji_no))
        print(str(emoji_yes))
        if str(reaction) == str(emoji_no):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Свадьба неудачна',
                            value=f'Время истекло или пользователь отказался от предложения',
                            inline=False)
            await ctx.send(embed=embed)
        if str(reaction) == str(emoji_yes):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Свадьба успешна',
                            value=f'{ctx.author.mention} и {member.mention} обвенчались.',
                            inline=False)
            await ctx.send(embed=embed)
            sql = "UPDATE marriage SET pair_id = ? WHERE user_id = ?"
            val = (member.id, ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            date_format = "%a, %d %b %Y %H:%M:%S"
            timestamp = datetime.now()
            date = timestamp.strftime(date_format)
            sql = "UPDATE marriage SET date = ? WHERE user_id = ?"
            val = (date, ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            sql = "UPDATE marriage SET pair_id = ? WHERE user_id = ?"
            val = (ctx.author.id, member.id)
            cursor.execute(sql, val)
            db.commit()
            sql = "UPDATE marriage SET date = ? WHERE user_id = ?"
            val = (date, member.id)
            cursor.execute(sql, val)
            db.commit()
            sql = "UPDATE money SET money = ? WHERE user_id = ?"
            val = (balance - 2000, ctx.author.id)
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
        raise error

    @commands.command(aliases=['divorce', 'развод'])
    async def __divorce(self, ctx):
        await ctx.send('ВНИМАНИЕ СЕЙЧАС ЗАПУЩЕНА ВЕРСИЯ БОТА ДЛЯ РАЗРАБОТКИ ВАШИ ДАННЫЕ НЕ БУДУТ СОХРАНЕНЫ')
        emoji_marry = self.client.get_emoji(995605076108382288)
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
        embed.add_field(name=f'{emoji_marry} Развод',
                        value=f'{ctx.author.name} и {user.name} теперь разведены и больше не пара')
        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    @commands.command(aliases=['lprofile', 'lp', 'lovep', 'loveprofile'])
    async def __lprofile(self, ctx):
        await ctx.send('ВНИМАНИЕ СЕЙЧАС ЗАПУЩЕНА ВЕРСИЯ БОТА ДЛЯ РАЗРАБОТКИ ВАШИ ДАННЫЕ НЕ БУДУТ СОХРАНЕНЫ')
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

    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.command(aliases=['lptop', 'lovetop', 'лавтоп', 'лптоп'])
    async def __love_leaderboard(self, ctx):
        await ctx.send('ВНИМАНИЕ СЕЙЧАС ЗАПУЩЕНА ВЕРСИЯ БОТА ДЛЯ РАЗРАБОТКИ ВАШИ ДАННЫЕ НЕ БУДУТ СОХРАНЕНЫ')
        async with ctx.channel.typing():
            counter = 0
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            users = []
            already_was = []
            for row in cursor.execute("SELECT user_id, pair_id, date FROM marriage ORDER BY date DESC LIMIT 15"):
                if row[2] != '0':
                    user = await self.client.fetch_user(row[0])
                    pair = await self.client.fetch_user(row[1])
                    if user not in already_was:
                        if pair not in already_was:
                            counter += 1
                            already_was.append(user)
                            if row[1] != 0:
                                pair = await self.client.fetch_user(row[1])
                                already_was.append(pair)

                                users.append(f'`#{counter}`. {user.mention} и : {pair.mention}, дата: {row[2]}\n')
            description = ' '.join([user for user in users])
            embed = nextcord.Embed(title='Топ 15 пар', color=settings['defaultBotColor'],
                                   timestamp=ctx.message.created_at, description=description)

            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(MarriageListener(client))
