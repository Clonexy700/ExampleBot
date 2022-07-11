import nextcord
from nextcord.ext import commands
import random
from config import settings
import sqlite3


class Emotions(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['поцеловать', 'цмок', 'цем', 'тьмок', 'kiss'])
    async def __kiss(self, ctx, user: nextcord.Member = None, *, message: str = None):
        emoji = "<a:emoji_1:995590858734841938>"
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}kiss <пользователь> [сообщение]')
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

        if balance < 5:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для отправки')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - 5, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        kissgifs = ["https://media1.tenor.com/images/896519dafbd82b9b924b575e3076708d/tenor.gif?itemid=8811697",
                    "https://media1.tenor.com/images/7fd98defeb5fd901afe6ace0dffce96e/tenor.gif?itemid=9670722",
                    "https://media1.tenor.com/images/78095c007974aceb72b91aeb7ee54a71/tenor.gif?itemid=5095865",
                    "https://media1.tenor.com/images/a390476cc2773898ae75090429fb1d3b/tenor.gif?itemid=12837192",
                    "https://media1.tenor.com/images/bc5e143ab33084961904240f431ca0b1/tenor.gif?itemid=9838409",
                    "https://media1.tenor.com/images/e858678426357728038c277598871d6d/tenor.gif?itemid=9903014",
                    "https://media1.tenor.com/images/a1f7d43752168b3c1dbdfb925bda8a33/tenor.gif?itemid=10356314",
                    "https://media1.tenor.com/images/8e0e0c3970262b0b4b30ee6d9eb04756/tenor.gif?itemid=12542720",
                    "https://media1.tenor.com/images/2f23c53755a5c3494a7f54bbcf04d1cc/tenor.gif?itemid=13970544",
                    "https://media1.tenor.com/images/c4ecd9b75be67ea56d5916c47ee3ad53/tenor.gif?itemid=14375353",
                    "https://media1.tenor.com/images/d1a11805180742c70339a6bfd7745f8d/tenor.gif?itemid=4883557",
                    "https://media1.tenor.com/images/6bd9c3ba3c06556935a452f0a3679ccf/tenor.gif?itemid=13387677",
                    "https://media1.tenor.com/images/04433eb0c31b175ab020cc9c6b94e1c4/tenor.gif?itemid=14686933",
                    "https://media1.tenor.com/images/d017f04c0383c3c6864d2a2ec414ea3d/tenor.gif?itemid=11293903",
                    "https://media1.tenor.com/images/ea9a07318bd8400fbfbd658e9f5ecd5d/tenor.gif?itemid=12612515",
                    "https://media1.tenor.com/images/e76e640bbbd4161345f551bb42e6eb13/tenor.gif?itemid=4829336",
                    "https://cdn.discordapp.com/attachments/624296774747553808/637901601209712640/kiss_3.gif",
                    "https://cdn.discordapp.com/attachments/624296774747553808/639093189017600000/21.gif",
                    "https://cdn.discordapp.com/attachments/624296774747553808/639093469121347595/29.gif",
                    "https://cdn.discordapp.com/attachments/621005423335702528/652822580310310924/JPEG_20190513_121707.jpg",
                    "https://cdn.discordapp.com/attachments/621005423335702528/652822932627652619/76_pLn7qnwk.jpg"
                    "https://cdn.discordapp.com/attachments/627524428447612949/655354838716121088/IwStTn6.gif"]
        description = f'**Поцелуй**\n{ctx.author.mention} ✧ {user.mention}'
        if message is not None:
            description = f'{description}\n{message}'
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=description)
        embed.set_author(name=self.client.user.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text='(ᴖ◡ᴖ)♪', icon_url=user.avatar.url)
        embed.set_image(random.choice(kissgifs))
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Emotions(client))
