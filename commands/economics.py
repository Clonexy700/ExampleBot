import nextcord
from nextcord.ext import commands
from nextcord.utils import get
import random
import datetime
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

        cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
            role_id INTERGER, guild_id INT, cost INTERGER
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

    @commands.cooldown(1, 3600 * 4, commands.BucketType.user)
    @commands.command(aliases=['moneydaily', 'ежедн', 'ежедневное', 'timely', 'еж', 'денежка', 'dailymoney',
                               'daily', 'награда', 'таймли', 'тайм', 'ежед', 'еже'])
    async def __daily(self, ctx):

        emoji = "<a:emoji_1:995590858734841938>"

        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance + 150, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=f'Вы получили __**150**__ {emoji}')
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/996084073569194084/996084305031872574/white_clock.png')
        embed.set_footer(text=f"Команду можно использовать раз в 4 часа\n{random.choice(settings['footers'])}",
                         icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @__daily.error
    async def daily_cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            remaining_time = str(datetime.timedelta(seconds=int(error.retry_after)))
            embed.add_field(name='Ошибка', value=f'Команда сейчас недоступна, '
                                                 f'попробуйте позже, через {remaining_time}')
            await ctx.send(embed=embed)
        raise error

    @commands.command(aliases=['bal', 'бал', 'баланс', 'money', 'balance', '$', 'wallet', 'мани', 'b', 'б'])
    async def __balance(self, ctx, user: nextcord.Member = None):
        emoji = self.client.get_emoji(settings['emoji_id'])
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

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=f"У вас на счету `{balance}` {emoji}")
        embed.set_author(name=f"Баланс пользователя: {user.name}", icon_url=user.avatar.url)
        embed.set_footer(text=random.choice(settings['footers']), icon_url=ctx.guild.icon)
        embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/512/6871/6871577.png')

        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.command(aliases=['give', 'transfer', 'дать', 'на', 'moneysend', 'sendmoney', 'send'])
    async def __transfer(self, ctx, user: nextcord.Member = None, amount: int = 0):
        emoji = self.client.get_emoji(settings['emoji_id'])
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
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для отправки')
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

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=f'Были отправлены __**{amount}**__ {emoji} на баланс {user.mention}')
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f'транзакция №{random.randint(1, 1000000000)}', icon_url=ctx.guild.avatar.url)

        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.command(aliases=['mleaderboard', 'mld', 'topmoney', 'mtop', 'topm', 'мтоп'])
    async def __money_leaderboard(self, ctx):
        emoji = self.client.get_emoji(settings['emoji_id'])
        async with ctx.channel.typing():
            counter = 0
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            users = []
            for row in cursor.execute("SELECT user_id, money FROM money ORDER BY money DESC LIMIT 15"):
                counter += 1
                user = await self.client.fetch_user(row[0])
                users.append(f'`#{counter}`. {user.mention}, `Баланс: {row[1]}` {emoji}\n')
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

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['take', 'withdraw', 'забрать'])
    async def __withdraw(self, ctx, user: nextcord.Member = None, amount: int = None):
        emoji = self.client.get_emoji(settings['emoji_id'])
        emoji = self.client.get_emoji(settings['emoji_id'])
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

        cursor.execute(f"SELECT money FROM money WHERE user_id = {user.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - amount, user.id)
        cursor.execute(sql, val)
        db.commit()

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.add_field(name='Валютные операции',
                        value=f'{ctx.author.mention} забрал у {user.mention} {amount} {emoji}')
        embed.set_footer(icon_url=user.avatar)

        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['award', 'наградить'])
    async def __award(self, ctx, user: nextcord.Member = None, amount: int = None):
        emoji = "<a:emoji_1:995590858734841938>"

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

        cursor.execute(f"SELECT money FROM money WHERE user_id = {user.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance + amount, user.id)
        cursor.execute(sql, val)
        db.commit()

        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.add_field(name='Валютные операции',
                        value=f'{ctx.author.mention} наградил пользователя {user.mention} {amount} {emoji}')
        embed.set_footer(icon_url=user.avatar)

        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    @commands.command(aliases=['slots', 'slot', 'casino', 'слоты'])
    async def __slots(self, ctx, amount: int = None):
        emoji = "<a:emoji_1:995590858734841938>"
        pink_gem = self.client.get_emoji(995991602822656061)
        orange_gem = self.client.get_emoji(995991591149895710)
        blue_gem = self.client.get_emoji(995991579502317568)
        green_gem = self.client.get_emoji(995991556798545961)
        purple_gem = self.client.get_emoji(995991536863035454)

        if amount is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды:\n'
                                                 f'{settings["PREFIX"]}slots <ставка>')
            return await ctx.send(embed=embed)
        if amount <= 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите количество валюты: '
                                                 f'{settings["PREFIX"]}give <пользователь> <количество>')
            return await ctx.send(embed=embed)
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if cursor.execute(f"SELECT user_id FROM money WHERE user_id = {ctx.author.id}").fetchone() is None:
            sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
            val = (ctx.author.id, 100)
            cursor.execute(sql, val)
            db.commit()

        cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        if balance < amount:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для отправки')
            return await ctx.send(embed=embed)

        first_row = []
        your_row = []
        third_row = []
        emoji_list = []
        emoji_list.append(pink_gem)
        emoji_list.append(orange_gem)
        emoji_list.append(blue_gem)
        emoji_list.append(green_gem)
        emoji_list.append(purple_gem)
        for i in range(3):
            emojii = random.choice(emoji_list)
            first_row.append(emojii)
            emojii = random.choice(emoji_list)
            your_row.append(emojii)
            emojii = random.choice(emoji_list)
            third_row.append(emojii)
        stater = f'Ставка: __**{amount}**__ {emoji} Выигрыш __**{int(0)}**__ {emoji}'
        if your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and your_row[
            0] == orange_gem:
            stater = f'Ставка: __**{amount}**__ {emoji} Выигрыш __**{int(amount * 6)}**__ {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n⠀|'
                                                                f'{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'|\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 6)}')
            sql = "UPDATE money SET money = ? WHERE user_id = ?"
            val = (balance + int(amount * 6), ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        elif your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and your_row[
            0] == purple_gem:
            stater = f'Ставка: __**{amount}**__ {emoji} Выигрыш __**{int(amount * 4)}**__ {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n⠀|'
                                                                f'{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'|\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 4)}')
            sql = "UPDATE money SET money = ? WHERE user_id = ?"
            val = (balance + int(amount * 4), ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        elif your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and your_row[
            0] != orange_gem and your_row[0] != purple_gem:
            stater = f'Ставка: __**{amount}**__ {emoji} Выигрыш __**{int(amount * 2.5)}**__ {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n⠀|'
                                                                f'{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'|\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 4)}')
            sql = "UPDATE money SET money = ? WHERE user_id = ?"
            val = (balance + int(amount * 2.5), ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        elif your_row[0] == your_row[1] or your_row[0] == your_row[2] or \
                your_row[2] == your_row[0] or your_row[1] == your_row[2]:
            stater = f'Ставка: __**{amount}**__ {emoji} Выигрыш __**{int(amount * 1.5)}**__ {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n⠀|'
                                                                f'{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'|\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 1.5)}')
            sql = "UPDATE money SET money = ? WHERE user_id = ?"
            val = (balance + int(amount * 1.5), ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=stater)
        embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n⠀|'
                                                            f'{your_row[0]} {your_row[1]} {your_row[2]}'
                                                            f'|\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
        embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance - amount)}')
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - amount, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        return await ctx.send(embed=embed)

    @commands.command(aliases=['gamble', 'гамбл'])
    async def __gamble(self, ctx, amount: int = None):
        emoji = "<a:emoji_1:995590858734841938>"
        if amount is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды:\n'
                                                 f'{settings["PREFIX"]}gamble <ставка>')
            return await ctx.send(embed=embed)
        if amount <= 0:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите количество валюты: '
                                                 f'{settings["PREFIX"]}gamble <ставка>')
            return await ctx.send(embed=embed)
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if cursor.execute(f"SELECT user_id FROM money WHERE user_id = {ctx.author.id}").fetchone() is None:
            sql = "INSERT INTO money(user_id, money) VALUES (?, ?)"
            val = (ctx.author.id, 100)
            cursor.execute(sql, val)
            db.commit()
        cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}")
        balance = cursor.fetchone()
        try:
            balance = balance[0]
        except:
            return await ctx.send('что-то с бд!!!')

        if balance < amount:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для отправки')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)

        user_strikes = random.randint(1, 15)
        bot_strikes = random.randint(4, 15)

        if user_strikes > bot_strikes:
            percentage = random.randint(50, 100)
            amount_won = int(amount * (percentage / 100))
            cursor.execute("UPDATE money SET money = ? WHERE user_id = ?",
                           (balance + amount_won, ctx.author.id))

            db.commit()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=f"Ты выиграл `{amount_won}` {emoji}\n Проценты: `{percentage}`\nВаш баланс: `{balance + amount_won}` {emoji}")
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        elif user_strikes < bot_strikes:
            percentage = random.randint(0, 80)
            amount_lost = int(amount * (percentage / 100))
            cursor.execute("UPDATE money SET money = ? WHERE user_id = ?",
                           (balance - amount_lost, ctx.author.id))

            db.commit()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=f"Ты проиграл `{amount_lost}` {emoji}\n `{percentage}`\nВаш баланс: `{balance - amount_lost}` {emoji}")
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        else:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=f"Ничья")
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        embed.add_field(name=f"**{ctx.author.name}**", value=f"Выбил число {user_strikes}")
        embed.add_field(name=f"**{ctx.bot.user.name}**", value=f"Выбил число {bot_strikes}")
        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    @commands.command(aliases=['add-shop', 'добавить', 'add'])
    async def __add_shop(self, ctx, role: nextcord.Role = None, cost: int = None):
        if role is None:
            return await ctx.send('hui')
        else:
            if cost is None:
                return await ctx.send('hui')
            elif cost < 0:
                return await ctx.send('hui')
            else:
                db = sqlite3.connect("./databases/main.sqlite")
                cursor = db.cursor()
                sql = "INSERT INTO shop(role_id, guild_id, cost) VALUES (?, ?, ?)"
                val = (role.id, ctx.guild.id, cost)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send('dobavila')

    @commands.command(aliases=['remove-shop', 'убрать', 'remove'])
    async def __remove_shop(self, ctx, role: nextcord.Role = None):
        if role is None:
            return await ctx.send('hui')
        else:
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            sql = f"DELETE FROM shop WHERE role_id = {role.id}"
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            await ctx.send('sdelala')

    @commands.command(aliases=['shop', 'market', 'магазин', 'маркет', 'шоп'])
    async def __market(self, ctx):
        emoji = "<a:emoji_1:995590858734841938>"
        async with ctx.channel.typing():
            counter = 0
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()

            roles = []
            for row in cursor.execute(f"SELECT role_id, cost FROM shop WHERE guild_id = {ctx.guild.id}"):
                role = ctx.guild.get_role(row[0])
                if role is not None:
                    counter += 1
                    roles.append(f'**{counter}**. {role.mention}\nСтоимость: __**{row[1]}**__ {emoji}\n')
            description = ' '.join([role for role in roles])
            embed = nextcord.Embed(title='Магазин ролей', color=settings['defaultBotColor'],
                                   timestamp=ctx.message.created_at, description=description)

            await ctx.send(embed=embed)

    @commands.command(aliases=['buy', 'buy-role', 'купить'])
    async def __buy(self, ctx, role: nextcord.Role):
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        if role is None:
            cursor.close()
            db.close()
            return await ctx.send('hui')
        else:
            if role in ctx.author.roles:
                cursor.close()
                db.close()
                return await ctx.send(f'u tebya uzhe est eta rol')

            elif cursor.execute(f"SELECT cost FROM shop WHERE role_id = {role.id}").fetchone()[0] > \
                    cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}").fetchone()[0]:
                cursor.close()
                db.close()
                return await ctx.send('hui')
            else:
                cost = cursor.execute(f"SELECT cost FROM shop WHERE role_id = {role.id}").fetchone()[0]
                await ctx.author.add_roles(role)
                cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}")
                balance = cursor.fetchone()
                try:
                    balance = balance[0]
                except:
                    return await ctx.send('что-то с бд!!!')

                sql = "UPDATE money SET money = ? WHERE user_id = ?"
                val = (balance - cost, ctx.author.id)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send('prodano i dano')


def setup(client):
    client.add_cog(Economics(client))
