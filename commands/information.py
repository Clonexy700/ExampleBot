import nextcord
from nextcord.ext import commands
import sqlite3
import locale
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from config import settings


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

            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.set_footer(text=f"ID: {user.id}")
            embed.set_thumbnail(url=user.avatar)
            embed.add_field(name="__**Главное:**__", value=f"**Имя:\n** {user}\n"
                                                           f"**Аккаунт создан:**\n "
                                                           f"{user.created_at.strftime(date_format)}\n")
            roles = ' '.join([r.mention for r in user.roles[1:]])
            if len(roles) > 900:
                roles = ' '.join([r.mention for r in user.roles[1:15]])
            embed.add_field(name="__**Информация, связанная с сервером:**__",
                            value=f"**Серверный никнейм:** {user.nick}\n"
                                  f"**Роли:** {roles}")

            # Свистопляски с целью вставки аватарки в Background.png, которая накладывается туда по типу маски и уже
            # готовое изображение постится самим ботом

            avatar = BytesIO()
            await user.display_avatar.with_format("png").save(avatar)

            avatar = Image.open(avatar)
            avatar = avatar.resize((130, 130))
            bigsize = (avatar.size[0] * 3, avatar.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(avatar.size, Image.ANTIALIAS)
            avatar.putalpha(mask)

            output = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            output.save('avatar.png')
            avatar = Image.open('avatar.png')
            fundo = Image.open('./assets/profile_backgrounds/background.png')
            fonte2 = ImageFont.truetype('ARIALUNI.TTF', 18)
            escrever = ImageDraw.Draw(fundo)

            db = sqlite3.connect("./databases/main.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT lvl, exp FROM levels WHERE user_id = {user.id}")
            leveling = cursor.fetchone()
            try:
                level = leveling[0]
                exp = leveling[1]
            except:
                return await ctx.send('что-то с бд!!!')

            cur_xp = exp
            cur_lvl = level
            next_xp = round((5 * (cur_lvl ** 3)) / 3)

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
            cursor.close()
            db.close()

            escrever.text(xy=(250, 70),
                          text=f'   Уровень: {cur_lvl} \n   {cur_xp}/{next_xp} XP\n   Время в войсах: {voice_time}\n   '
                               f'Баланс: {balance}\n На сервер присоединился:\n '
                               f'{user.joined_at.strftime(date_format)}\n',
                          fill=(255, 255, 255), font=fonte2)
            escrever.text(xy=(230, 24), text=f'Профиль: {user.name}', fill=(255, 255, 255),
                          font=fonte2)
            fundo.paste(avatar, (40, 90), avatar)
            bv = BytesIO()
            fundo.save(bv, "PNG", quality=100)
            bv.seek(0)
            file = nextcord.File(bv, filename="bv.png")

            await ctx.send(embed=embed, file=file)


def setup(client):
    client.add_cog(InformationSender(client))
