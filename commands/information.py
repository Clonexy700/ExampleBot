import nextcord
from nextcord.ext import commands
import sqlite3
import locale
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from config import settings
from easy_pil import *


class InformationSender(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['i', 'инфо', 'инф', 'info', 'о', 'я', 'профиль', 'profile', 'me'])
    async def __info(self, ctx, user: nextcord.Member = None):
        async with ctx.channel.typing():

            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
            date_format = "%a, %d %b %Y %H:%M:%S"

            if user is None:
                user = ctx.author

            star = self.client.get_emoji(996245796099997756)
            info = self.client.get_emoji(996245800613052486)
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.set_footer(text=f"ID: {user.id}\nКоманду вызвал: {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embed.add_field(name=f'{info} Аккаунт создан', value=f'```\n{user.created_at.strftime(date_format)}\n```',
                            inline=False)
            roles = ' '.join([r.mention for r in user.roles[1:]])
            if len(roles) > 900:
                roles = ' '.join([r.mention for r in user.roles[1:15]])
            # Свистопляски с целью вставки аватарки в Background.png, которая накладывается туда по типу маски и уже
            # готовое изображение постится самим ботом

            background = Editor('./assets/profile_backgrounds/background.png')
            avatar = BytesIO()
            await user.display_avatar.with_format("png").save(avatar)
            profile_picture = Image.open(avatar)
            profile = Editor(profile_picture).resize((550, 550)).rounded_corners(radius=50)
            larger_font = Font('ARIALUNI.TTF', 65)
            font = Font('ARIALUNI.TTF', 50)
            background.paste(profile, (250, 300))
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT lvl, exp FROM levels WHERE user_id = {user.id}")
            leveling = cursor.fetchone()
            level = leveling[0]
            exp = leveling[1]

            cur_xp = exp
            cur_lvl = level
            next_xp = round((3000 * (cur_lvl ** 2)))
            voice_time = cursor.execute(f"SELECT time FROM voice WHERE user_id = {user.id}").fetchone()[0]

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
            warn_count = cursor.execute(f"SELECT warns FROM warns WHERE user_id = {user.id}").fetchone()[0]
            cursor.close()
            db.close()
            background.text((1250, 310), str(user), font=larger_font, color="#FFFFFF")
            background.text((1250, 425), f"УРОВЕНЬ: {cur_lvl}, ОПЫТ: {cur_xp}/{next_xp}", font=font, color="#FFFFFF")
            background.text((1250, 525), f"ВРЕМЯ В ВОЙСАХ: {voice_time}", font=font, color="#FFFFFF")
            background.text((1250, 630), f"БАЛАНС: {balance}", font=font, color="#FFFFFF")
            background.text((1250, 735), f"{user.joined_at.strftime(date_format)}", font=font, color="#FFFFFF")
            background.text((1250, 835), f"ВАРНЫ: {warn_count}", font=font, color="#FFFFFF")
            embed.add_field(name=f'{star} На сервер присоединился:',
                            value=f'```\n{user.joined_at.strftime(date_format)}\n```',
                            inline=False)
            voice = self.client.get_emoji(996245791947624528)
            level = self.client.get_emoji(996245798801129473)
            credit_card = self.client.get_emoji(996245797416996895)
            role = self.client.get_emoji(996245790357999646)
            embed.add_field(name=f"{level} Уровень", value=f'```\n{cur_lvl}\n{cur_xp}|{next_xp}\n```', inline=True)
            embed.add_field(name=f'{credit_card} Баланс:', value=f'```{balance}```', inline=True)
            embed.add_field(name=f"{voice} Время в войсах", value=f"```{voice_time}```", inline=True)
            embed.add_field(name=f"{role} Роли", value=roles, inline=True)
            file = nextcord.File(fp=background.image_bytes, filename="bv.png")
            embed.set_image(url="attachment://bv.png")
            await ctx.send(embed=embed, file=file)


def setup(client):
    client.add_cog(InformationSender(client))
