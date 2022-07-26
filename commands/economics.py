from typing import Optional
import nextcord
from nextcord import Interaction, SlashOption, Permissions
from nextcord.ui import Button, View
from nextcord.ext import commands
from nextcord.utils import get
import random
import datetime
from random import shuffle
import sqlite3
from config import settings
from core.games.blackjack import Hand, Deck, check_for_blackjack, show_blackjack_results, player_is_over, \
    cards_emoji_representation, create_deck, deal_starting_cards, create_blackjack_embed, create_final_view, \
    maybe_blackjack_cards, create_game_start_blackjack_embed
from core.money.updaters import update_user_balance
from core.money.getters import get_user_balance
from core.ui.buttons import create_button, ViewAuthorCheck
import asyncio
from collections import Counter


def most_frequent(List: list):
    counter = 0
    num = List[0]

    for i in List:
        curr_frequency = List.count(i)
        if curr_frequency > counter:
            counter = curr_frequency
            num = i

    return counter, num


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

        cursor.execute("""CREATE TABLE IF NOT EXISTS jackpot (guild_id INTERGER, amount INTERGER)""")
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
        cursor.execute(f"SELECT amount FROM jackpot WHERE guild_id = {message.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO jackpot(guild_id, amount) VALUES (?, ?)"
            val = (message.guild.id, 10000)
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
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/996084073569194084/996165596397981706/Picsart_22-07-12_00-25-50-038.png')
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
        emoji = "<a:emoji_1:995590858734841938>"
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
                               description=f"У вас на счету __**{balance}**__ {emoji}")
        embed.set_author(name=f"Баланс пользователя: {user.name}", icon_url=user.display_avatar)
        embed.set_footer(text=random.choice(settings['footers']), icon_url=ctx.guild.icon)

        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.command(aliases=['give', 'transfer', 'дать', 'на', 'moneysend', 'sendmoney', 'send'])
    async def __transfer(self, ctx, user: nextcord.Member = None, amount: int = 0):
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
        embed.set_footer(text=f'транзакция №{random.randint(1, 1000000000)}', icon_url=ctx.guild.icon.url)

        await ctx.send(embed=embed)

        cursor.close()
        db.close()

    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.command(aliases=['mleaderboard', 'mld', 'topmoney', 'mtop', 'topm', 'мтоп'])
    async def __money_leaderboard(self, ctx):
        emoji = "<a:emoji_1:995590858734841938>"
        async with ctx.channel.typing():
            counter = 0
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            users = []
            for row in cursor.execute("SELECT user_id, money FROM money ORDER BY money DESC LIMIT 15"):
                counter += 1
                try:
                    user = get(ctx.guild.members, id=row[0])
                except:
                    pass
                try:
                    users.append(f'**{counter}**. {user.mention}\n__**Баланс**__: `{row[1]}` {emoji}\n')
                except:
                    pass
            description = ' '.join([user for user in users])
            embed = nextcord.Embed(title='Топ 15 сервера по валюте', color=settings['defaultBotColor'],
                                   timestamp=ctx.message.created_at, description=description)
            embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)

            cursor.close()
            db.close()
            await ctx.send(embed=embed)

    @__money_leaderboard.error
    async def money_leaderboard_cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value='Команда сейчас недоступна, '
                                                 'попробуйте позже, через %.2fs секунд' % error.retry_after)
            await ctx.send(embed=embed)
        raise error

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['take', 'забрать'])
    async def ___withdraw(self, ctx, user: nextcord.Member = None, amount: int = None):
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

    @commands.command(aliases=['slots', 'slot', 'casino', 'слоты', 'казино'])
    async def __slots(self, ctx, amount: int = None):
        emoji = "<a:emoji_1:995590858734841938>"
        pink_gem = self.client.get_emoji(995991602822656061)
        orange_gem = self.client.get_emoji(995991591149895710)
        blue_gem = self.client.get_emoji(995991579502317568)
        green_gem = self.client.get_emoji(995991556798545961)
        purple_gem = self.client.get_emoji(995991536863035454)
        random.seed(random.randint(1, 9941287654123444254))

        if amount is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды:\n'
                                                 f'{settings["PREFIX"]}slots <ставка>')
            return await ctx.send(embed=embed)
        if amount < 50:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Укажите ставку больше чем **50** {emoji}\n '
                                                 f'{settings["PREFIX"]}slots <ставка>')
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

        jackpot = False

        first_row = []
        your_row = []
        third_row = []
        emoji_list = [pink_gem, orange_gem, blue_gem, green_gem, purple_gem]
        emoji_list_2 = [pink_gem, blue_gem, green_gem, purple_gem]
        emoji_list_3 = [pink_gem, blue_gem, green_gem]
        amount_win = 0
        random.seed(random.randint(1, 3131293129329131))
        percentage = random.random()
        if percentage < 0.3:
            player_will_choose_from = emoji_list
        elif percentage < 0.6:
            player_will_choose_from = emoji_list_2
        else:
            player_will_choose_from = emoji_list_3
        today_we_try_to_roll_second = random.random()
        today_maybe_win_slot_1 = random.random()
        today_maybe_win_slot_2 = random.random()
        free_spin = random.random()
        print(free_spin)
        shuffle(emoji_list)
        for i in range(3):
            if ctx.author.id != 314618320093577217:
                first_row.append(random.choice(emoji_list))
                third_row.append(random.choice(emoji_list))
                if i == 0:
                    your_row.append(random.choice(player_will_choose_from))
                if i == 1:
                    if today_maybe_win_slot_1 < 0.35:
                        your_row.append(random.choice(player_will_choose_from))
                    else:
                        emoji_choose = random.choice(player_will_choose_from)
                        while emoji_choose in your_row:
                            emoji_choose = random.choice(player_will_choose_from)
                        your_row.append(emoji_choose)
                if i == 2:
                    if today_we_try_to_roll_second < 0.9:
                        if today_maybe_win_slot_2 < 0.25:
                            your_row.append(random.choice(player_will_choose_from))
                        else:
                            emoji_choose = random.choice(player_will_choose_from)
                            while emoji_choose in your_row:
                                emoji_choose = random.choice(player_will_choose_from)
                            your_row.append(emoji_choose)
                    else:
                        emoji_choose = random.choice(player_will_choose_from)
                        while emoji_choose in your_row:
                            emoji_choose = random.choice(player_will_choose_from)
                        your_row.append(emoji_choose)
            else:
                first_row.append(orange_gem)
                third_row.append(orange_gem)
                your_row.append(random.choice(player_will_choose_from))
        board = [your_row[0], your_row[1], your_row[2],
                 first_row[0], first_row[1], first_row[2],
                 third_row[0], third_row[1], third_row[2]]
        stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
        if your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and your_row[
            0] == orange_gem:
            amount_win += int(amount*4)
            stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                                                f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 4)}')
        elif your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and your_row[
            0] == purple_gem:
            amount_win += int(amount*3)
            stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                                                f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 3)}')
        elif your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and your_row[
            0] != orange_gem and your_row[0] != purple_gem:
            amount_win += int(amount*2)
            stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                                                f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 2)}')
        elif your_row[0] == your_row[1] or your_row[1] == your_row[2] or your_row[0] == your_row[2]:
            amount_win += int(amount*1)
            stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                                                f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance + amount * 1)}')
        else:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=stater)
            embed.add_field(name=f'Слоты - {ctx.author}', value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                                                f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                                                f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
            embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {int(balance - amount)}')
        free_spin_state = False
        times, gem = most_frequent(board)
        if times >= 7:
            jackpot = True
        if free_spin < 0.25:
            embed.add_field(name='Бесплатные прокрутки барабана', value=f'Барабан будет крутиться столько раз, сколько на поле максимально выпало кристаллов.'
                                                                        f', так как на поле больше всего {gem}, то количество бесплатных прокруток барабана: **{times}**'
                                                                        f' Поражения отображаться не будут')
            free_spin_state = True
        if free_spin_state is True:
            for j in range(times):
                first_row = []
                your_row = []
                third_row = []
                emoji_list = [pink_gem, orange_gem, blue_gem, green_gem, purple_gem]
                emoji_list_2 = [pink_gem, blue_gem, green_gem, purple_gem]
                emoji_list_3 = [pink_gem, blue_gem, green_gem]
                random.seed(random.randint(1, 3131293129329131))
                percentage = random.random()
                if percentage < 0.3:
                    player_will_choose_from = emoji_list
                elif percentage < 0.6:
                    player_will_choose_from = emoji_list_2
                else:
                    player_will_choose_from = emoji_list_3
                today_we_try_to_roll_second = random.random()
                today_maybe_win_slot_1 = random.random()
                today_maybe_win_slot_2 = random.random()
                shuffle(emoji_list)
                for i in range(3):
                    first_row.append(random.choice(emoji_list))
                    third_row.append(random.choice(emoji_list))
                    if i == 0:
                        your_row.append(random.choice(player_will_choose_from))
                    if i == 1:
                        if today_maybe_win_slot_1 < 0.95:
                            your_row.append(random.choice(player_will_choose_from))
                        else:
                            emoji_choose = random.choice(player_will_choose_from)
                            while emoji_choose in your_row:
                                emoji_choose = random.choice(player_will_choose_from)
                            your_row.append(emoji_choose)
                    if i == 2:
                        if today_we_try_to_roll_second < 0.9:
                            if today_maybe_win_slot_2 < 0.85:
                                your_row.append(random.choice(player_will_choose_from))
                            else:
                                emoji_choose = random.choice(player_will_choose_from)
                                while emoji_choose in your_row:
                                    emoji_choose = random.choice(player_will_choose_from)
                                your_row.append(emoji_choose)
                        else:
                            emoji_choose = random.choice(player_will_choose_from)
                            while emoji_choose in your_row:
                                emoji_choose = random.choice(player_will_choose_from)
                            your_row.append(emoji_choose)
                amount_win += int(0)
                stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
                if your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and \
                        your_row[
                            0] == orange_gem:
                    amount_win += int(amount * 4)
                    stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
                    embed.add_field(name=f'Бесплатная прокрутка {j+1} - {ctx.author}',
                                    value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                          f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                          f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
                elif your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and \
                        your_row[
                            0] == purple_gem:
                    amount_win += int(amount * 3)
                    stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
                    embed.add_field(name=f'Бесплатная прокрутка {j+1} - {ctx.author}',
                                    value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                          f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                          f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
                elif your_row[0] == your_row[1] and your_row[1] == your_row[2] and your_row[2] == your_row[0] and \
                        your_row[
                            0] != orange_gem and your_row[0] != purple_gem:
                    amount_win += int(amount * 2)
                    stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
                    embed.add_field(name=f'Бесплатная прокрутка {j+1} - {ctx.author}',
                                    value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                          f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                          f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
                elif your_row[0] == your_row[1] or your_row[1] == your_row[2] or your_row[0] == your_row[2]:
                    amount_win += int(amount * 1)
                    stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
                    embed.add_field(name=f'Бесплатная прокрутка {j+1} - {ctx.author}',
                                    value=f'⠀{first_row[0]} {first_row[1]} {first_row[2]}\n'
                                          f'⠀{your_row[0]} {your_row[1]} {your_row[2]}'
                                          f'\n⠀{third_row[0]} {third_row[1]} {third_row[2]}')
                else:
                    pass

                board = [your_row[0], your_row[1], your_row[2],
                         first_row[0], first_row[1], first_row[2],
                         third_row[0], third_row[1], third_row[2]]
                times, gem = most_frequent(board)
                if times >= 7:
                    jackpot = True

        if jackpot is False:
            jackpot_amount = cursor.execute(f"SELECT amount FROM jackpot WHERE guild_id = {ctx.guild.id}").fetchone()[0]
            jack_to_footer = jackpot_amount
            if amount_win == 0:
                sql = "UPDATE jackpot SET amount = ? WHERE guild_id = ?"
                val = (jackpot_amount+amount, ctx.guild.id)
                cursor.execute(sql, val)
                db.commit()
                jack_to_footer = jackpot_amount + amount
        if jackpot is True:
            embed.add_field(name="JACKPOT WIN", value=f'{ctx.author.name} забирает джекпот!')
            jackpot_amount = cursor.execute(f"SELECT amount FROM jackpot WHERE guild_id = {ctx.guild.id}").fetchone()[0]
            sql = "UPDATE jackpot SET amount = ? WHERE guild_id = ?"
            val = (10000, ctx.guild.id)
            cursor.execute(sql, val)
            db.commit()
            amount_win += jackpot_amount
            jack_to_footer = 10000

        if amount_win == 0:
            sql = "UPDATE money SET money = ? WHERE user_id = ?"
            val = (balance - amount, ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
        else:
            sql = "UPDATE money SET money = ? WHERE user_id = ?"
            print(amount_win)
            val = (balance + amount_win, ctx.author.id)
            cursor.execute(sql, val)
            db.commit()
        stater = f'Ставка: **{amount}** {emoji} Выигрыш **{amount_win}** {emoji}'
        embed.description = stater
        embed.set_footer(icon_url=ctx.author.avatar.url, text=f'Ваш баланс {get_user_balance(ctx.author.id)}'
                                                              f'\nРазмер Джекпота теперь составляет: {jack_to_footer}')
        await ctx.send(embed=embed)
        cursor.close()
        db.close()

    @__slots.error
    async def __slots_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value='Команда сейчас недоступна, '
                                                 'попробуйте позже, через %.2fs секунд' % error.retry_after)
            await ctx.send(embed=embed)
        raise error

    @commands.cooldown(1, 7, commands.BucketType.user)
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
            percentage = random.randint(0, 95)
            amount_lost = int(amount * (percentage / 100))
            cursor.execute("UPDATE money SET money = ? WHERE user_id = ?",
                           (balance - amount_lost, ctx.author.id))

            db.commit()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                   description=f"Ты проиграл `{amount_lost}` {emoji}\n Проценты: `{percentage}`\nВаш баланс: `{balance - amount_lost}` {emoji}")
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

    @__gamble.error
    async def gamble_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value='Команда сейчас недоступна, '
                                                 'попробуйте позже, через %.2fs секунд' % error.retry_after)
            await ctx.send(embed=embed)
        raise error

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['add-shop', 'добавить', 'add'])
    async def __add_shop(self, ctx, role: nextcord.Role = None, cost: int = None):
        if role is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды:\n'
                                                 f'{settings["PREFIX"]}добавить <роль> <цена>')
            return await ctx.send(embed=embed)
        else:
            if cost is None:
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'Правильное написание команды:\n'
                                                     f'{settings["PREFIX"]}добавить <роль> <цена>')
                return await ctx.send(embed=embed)
            elif cost < 0:
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'Цена не может быть отрицательной')
                return await ctx.send(embed=embed)
            else:
                db = sqlite3.connect("./databases/main.sqlite")
                cursor = db.cursor()
                sql = "INSERT INTO shop(role_id, guild_id, cost) VALUES (?, ?, ?)"
                val = (role.id, ctx.guild.id, cost)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Магазин', value=f'Роль {role.mention} была успешно добавлена в магазин')
                embed.set_footer(text=random.choice(settings['footers']), icon_url=ctx.guild.icon)
                await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['remove-shop', 'убрать', 'remove'])
    async def __remove_shop(self, ctx, role: nextcord.Role = None):
        if role is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды:\n'
                                                 f'{settings["PREFIX"]}убрать <роль>')
            return await ctx.send(embed=embed)
        else:
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            sql = f"DELETE FROM shop WHERE role_id = {role.id}"
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Магазин', value=f'Роль {role.mention} была успешно убрана из магазина')
            embed.set_footer(text=random.choice(settings['footers']), icon_url=ctx.guild.icon)
            await ctx.send(embed=embed)

    @commands.command(aliases=['shop', 'market', 'магазин', 'маркет', 'шоп'])
    async def __market(self, ctx):
        emoji = "<a:emoji_1:995590858734841938>"
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
        if len(roles) == 0:
            description = 'Тут ничего нет...'
        embed = nextcord.Embed(title='Магазин', color=settings['defaultBotColor'],
                               timestamp=ctx.message.created_at, description=description)
        embed.set_footer(text=random.choice(settings['footers']), icon_url=ctx.guild.icon)
        await ctx.send(embed=embed)

    @commands.command(aliases=['buy', 'buy-role', 'купить'])
    async def __buy(self, ctx, number_of_role: int):
        emoji = "<a:emoji_1:995590858734841938>"
        db = sqlite3.connect("./databases/main.sqlite")
        cursor = db.cursor()
        roles = []
        try:
            for row in cursor.execute(f"SELECT role_id, cost FROM shop WHERE guild_id = {ctx.guild.id}"):
                role = ctx.guild.get_role(row[0])
                roles.append(role)
        except:
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Возникла ошибка, может в магазине нет ролей или такой роли?')
            return await ctx.send(embed=embed)
        if len(roles) < number_of_role:
            cursor.close()
            db.close()
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Возникла ошибка, может в магазине нет ролей или такой роли?')
            return await ctx.send(embed=embed)
        else:
            if roles[number_of_role - 1] in ctx.author.roles:
                cursor.close()
                db.close()
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'У вас уже есть эта роль, нельзя купить её снова!')
                return await ctx.send(embed=embed)

            elif cursor.execute(f"SELECT cost FROM shop WHERE role_id = {roles[number_of_role - 1].id}").fetchone()[0] > \
                    cursor.execute(f"SELECT money FROM money WHERE user_id = {ctx.author.id}").fetchone()[0]:
                cursor.close()
                db.close()
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для покупки')
                return await ctx.send(embed=embed)
            else:
                cost = \
                    cursor.execute(f"SELECT cost FROM shop WHERE role_id = {roles[number_of_role - 1].id}").fetchone()[
                        0]
                await ctx.author.add_roles(roles[number_of_role - 1])
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
                embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                embed.add_field(name='Магазин', value=f'Роль {roles[number_of_role - 1].mention} была куплена.')
                embed.set_footer(text=f"остаточный баланс после операции: {balance - cost}", icon_url=ctx.guild.icon)
                await ctx.send(embed=embed)

    @nextcord.slash_command(name='blackjack',
                            default_member_permissions=Permissions(send_messages=True))
    async def __blackjack(self, interaction: Interaction, bet: Optional[int] = SlashOption(required=True)):
        if bet <= 0:
            return await interaction.response.send_message('negative_value_error')
        balance = get_user_balance(interaction.user.id)
        if balance < bet:
            return await interaction.response.send_message('not_enough_money_error')
        global player
        player = interaction.user
        await interaction.response.defer()
        deck = create_deck()
        player_hand = Hand()
        dealer_hand = Hand(dealer=True)
        deal_starting_cards(player_hand, dealer_hand, deck)
        global turn
        turn = 1

        async def hit_callback(interaction: Interaction):
            global turn
            turn += 1
            player_hand.add_card(deck.deal())
            if player_is_over(player_hand):
                update_user_balance(interaction.user.id, -bet)
                balance = get_user_balance(interaction.user.id)
                msg = "Ваш баланс"
                embed = create_blackjack_embed(self.client, "**Дилер** победил", player_hand, dealer_hand,
                                               f'{msg} {balance}', interaction.user.display_avatar)
                view = create_final_view()
                await interaction.message.edit(embed=embed, view=view)
            else:
                embed = create_game_start_blackjack_embed(self.client, f"ход {turn}", player_hand, dealer_hand)
                await interaction.message.edit(embed=embed)

        async def stand_callback(interaction: Interaction):
            global turn
            turn += 1
            while dealer_hand.get_value() < 17:
                dealer_hand.add_card(deck.deal())
                if player_is_over(dealer_hand):
                    update_user_balance(interaction.user.id, bet)
                    balance = get_user_balance(interaction.user.id)
                    msg = "Ваш баланс"
                    embed = create_blackjack_embed(self.client, f"**{interaction.user.mention}** победил",
                                                   player_hand, dealer_hand,
                                                   f'{msg} {balance}', interaction.user.display_avatar)
                    view = create_final_view()
                    await interaction.message.edit(embed=embed, view=view)
            if 17 <= dealer_hand.get_value() <= 21:
                if dealer_hand.get_value() > player_hand.get_value():
                    update_user_balance(interaction.user.id, -bet)
                    balance = get_user_balance(interaction.user.id)
                    msg = "Ваш баланс"
                    embed = create_blackjack_embed(self.client, "**Дилер** победил", player_hand, dealer_hand,
                                                   f'{msg} {balance}', interaction.user.display_avatar)
                    view = create_final_view()
                    await interaction.message.edit(embed=embed, view=view)
                elif dealer_hand.get_value() == player_hand.get_value():
                    embed = create_blackjack_embed(self.client, "**Ничья**", player_hand, dealer_hand)
                    view = create_final_view()
                    await interaction.message.edit(embed=embed, view=view)
                else:
                    update_user_balance(interaction.user.id, bet)
                    balance = get_user_balance(interaction.user.id)
                    msg = "Ваш баланс"
                    embed = create_blackjack_embed(self.client, f"**{interaction.user.mention}** победил",
                                                   player_hand, dealer_hand,
                                                   f'{msg} {balance}', interaction.user.display_avatar)
                    view = create_final_view()
                    await interaction.message.edit(embed=embed, view=view)

        async def dealer_blackjack_callback(interaction: Interaction):
            if check_for_blackjack(dealer_hand):
                embed = create_blackjack_embed(self.client, "**Ничья**", player_hand, dealer_hand)
                view = create_final_view()
                await interaction.message.edit(embed=embed, view=view)
            else:
                update_user_balance(interaction.user.id, int(bet * 1.5))
                balance = get_user_balance(interaction.user.id)
                msg = "Ваш баланс"
                embed = create_blackjack_embed(self.client, f"**{interaction.user.mention}** победил",
                                               player_hand, dealer_hand,
                                               f'{msg} {balance}', interaction.user.display_avatar)
                view = create_final_view()
                await interaction.message.edit(embed=embed, view=view)

        async def one_to_one_callback(interaction: Interaction):
            update_user_balance(interaction.user.id, bet)
            balance = get_user_balance(interaction.user.id)
            msg = "Ваш баланс"
            embed = create_blackjack_embed(self.client, f"**{interaction.user.mention}** берёт 1:1",
                                           player_hand, dealer_hand,
                                           f'{msg} {balance}', interaction.user.display_avatar)
            view = create_final_view()
            await interaction.message.edit(embed=embed, view=view)

        if check_for_blackjack(player_hand):
            if str(dealer_hand.cards[1]) in maybe_blackjack_cards:
                dealer_blackjack = create_button("Проверка блекджека", dealer_blackjack_callback, False)
                one_to_one = create_button("взять 1:1", one_to_one_callback, False)
                view = ViewAuthorCheck(interaction.user)
                view.add_item(dealer_blackjack)
                view.add_item(one_to_one)

                embed = create_game_start_blackjack_embed(self.client, f"ход {turn}", player_hand, dealer_hand)
                await interaction.followup.send(embed=embed, view=view)
            else:
                update_user_balance(interaction.user.id, int(bet * 1.5))
                balance = get_user_balance(interaction.user.id)
                msg = "Ваш баланс"
                embed = create_blackjack_embed(self.client, f"**{interaction.user.mention}** победил",
                                               player_hand, dealer_hand,
                                               f'{msg} {balance}', interaction.user.display_avatar)
                view = create_final_view()
                await interaction.followup.send(embed=embed, view=view)
        else:
            if check_for_blackjack(dealer_hand):
                update_user_balance(interaction.user.id, -bet)
                balance = get_user_balance(interaction.user.id)
                msg = "Ваш баланс"
                embed = create_blackjack_embed(self.client, "**Dealer** победил", player_hand, dealer_hand,
                                               f'{msg} {balance}', interaction.user.display_avatar)
                view = create_final_view()
                await interaction.followup.send(embed=embed, view=view)
            else:
                hit = create_button("Ещё", hit_callback, False)
                stand = create_button("Хватит", stand_callback, False)
                view = ViewAuthorCheck(interaction.user)
                view.add_item(hit)
                view.add_item(stand)

                embed = create_game_start_blackjack_embed(self.client, f"ход {turn}", player_hand, dealer_hand)
                await interaction.followup.send(embed=embed, view=view)


def setup(client):
    client.add_cog(Economics(client))
