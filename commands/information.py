import nextcord
from nextcord.ext import commands
import sqlite3
import locale
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from config import settings
from easy_pil import *


def format_seconds_to_hhmmss(seconds):
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)


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
            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()
            warn_count = cursor.execute(f"SELECT warns FROM warns WHERE user_id = {user.id}").fetchone()[0]
            if warn_count == 0:
                background = Editor('./assets/profile_backgrounds/bg.png')
            elif warn_count == 1:
                background = Editor('./assets/profile_backgrounds/bg_2.png')
            else:
                background = Editor('./assets/profile_backgrounds/bg_3.png')
            avatar = BytesIO()
            await user.display_avatar.with_format("png").save(avatar)
            profile_picture = Image.open(avatar)
            profile = Editor(profile_picture).resize((360, 360)).rounded_corners(radius=50)
            larger_font = Font('ARIALUNI.TTF', 65)
            font = Font('ARIALUNI.TTF', 50)
            background.paste(profile, (230, 360))
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
            cursor.execute(f"SELECT pair_id FROM marriage WHERE user_id = {ctx.author.id}")
            partner = cursor.fetchone()
            try:
                partner = partner[0]
            except:
                return await ctx.send('что-то с бд!!!')
            if partner == 0:
                partner_text = '-'
            else:
                partner_text = await self.client.fetch_user(partner)
                partner_text = partner_text.name
            cursor.close()
            db.close()
            background.text((550, 765), str(user.name), font=font, color="#FFFFFF")
            background.text((450, 865), str(partner_text), font=font, color="#FFFFFF")
            background.text((1200, 935), f"{cur_lvl} LVL", font=font, color="#FFFFFF")
            background.text((1200, 835), f"{format_seconds_to_hhmmss(float(voice_time))}", font=font, color="#FFFFFF")
            background.text((1200, 735), f"{balance}", font=font, color="#FFFFFF")
            background.text((1000, 465), f"{user.joined_at.strftime(date_format)}", font=font, color="#FFFFFF")
            background.text((1000, 585), f"{user.created_at.strftime(date_format)}", font=font, color="#FFFFFF")
            embed.add_field(name=f'{star} На сервер присоединился:',
                            value=f'```\n{user.joined_at.strftime(date_format)}\n```',
                            inline=False)
            voice = self.client.get_emoji(996245791947624528)
            level = self.client.get_emoji(996245798801129473)
            credit_card = self.client.get_emoji(996245797416996895)
            role = self.client.get_emoji(996245790357999646)
            embed.add_field(name=f"{level} Уровень", value=f'```\n{cur_lvl}\n{cur_xp}|{next_xp}\n```', inline=True)
            embed.add_field(name=f'{credit_card} Баланс:', value=f'```{balance}```', inline=True)
            embed.add_field(name=f"{voice} Время в войсах",
                            value=f"```{format_seconds_to_hhmmss(float(voice_time))}```", inline=True)
            embed.add_field(name=f"{role} Роли", value=roles, inline=True)
            file = nextcord.File(fp=background.image_bytes, filename="bv.png")
            embed.set_image(url="attachment://bv.png")
            await ctx.send(embed=embed, file=file)


def setup(client):
    client.add_cog(InformationSender(client))
