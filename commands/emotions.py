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
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для использования команды, все команды эмоций стоят 5 {emoji}')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - 5, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        gifs = ["https://media1.tenor.com/images/896519dafbd82b9b924b575e3076708d/tenor.gif?itemid=8811697",
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
        embed.set_image(random.choice(gifs))
        await ctx.send(embed=embed)

    @commands.command(aliases=['hug', 'обнять', 'обнимашки'])
    async def __hug(self, ctx, user: nextcord.Member=None, *, message: str = None):
        emoji = "<a:emoji_1:995590858734841938>"
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}hug <пользователь> [сообщение]')
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
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для использования команды, все команды эмоций стоят 5 {emoji}')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - 5, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        gifs = ["https://media1.tenor.com/images/5845f40e535e00e753c7931dd77e4896/tenor.gif?itemid=9920978",
                   "https://media1.tenor.com/images/6db54c4d6dad5f1f2863d878cfb2d8df/tenor.gif?itemid=7324587",
                   "https://media1.tenor.com/images/b0de026a12e20137a654b5e2e65e2aed/tenor.gif?itemid=7552093",
                   "https://media1.tenor.com/images/e58eb2794ff1a12315665c28d5bc3f5e/tenor.gif?itemid=10195705",
                   "https://media1.tenor.com/images/7db5f172665f5a64c1a5ebe0fd4cfec8/tenor.gif?itemid=9200935",
                   "https://media1.tenor.com/images/4d89d7f963b41a416ec8a55230dab31b/tenor.gif?itemid=5166500",
                   "https://media1.tenor.com/images/506aa95bbb0a71351bcaa753eaa2a45c/tenor.gif?itemid=7552075",
                   "https://media1.tenor.com/images/074d69c5afcc89f3f879ca473e003af2/tenor.gif?itemid=4898650",
                   "https://media1.tenor.com/images/1069921ddcf38ff722125c8f65401c28/tenor.gif?itemid=11074788",
                   "https://media1.tenor.com/images/18474dc6afa97cef50ad53cf84e37d08/tenor.gif?itemid=12375072",
                   "https://media1.tenor.com/images/460c80d4423b0ba75ed9592b05599592/tenor.gif?itemid=5044460",
                   "https://media1.tenor.com/images/42922e87b3ec288b11f59ba7f3cc6393/tenor.gif?itemid=5634630",
                   "https://media1.tenor.com/images/44b4b9d5e6b4d806b6bcde2fd28a75ff/tenor.gif?itemid=9383138",
                   "https://media1.tenor.com/images/45b1dd9eaace572a65a305807cfaec9f/tenor.gif?itemid=6238016",
                   "https://media1.tenor.com/images/b7487d45af7950bfb3f7027c93aa49b1/tenor.gif?itemid=9882931",
                   "https://media1.tenor.com/images/79c461726e53ee8f9a5a36521f69d737/tenor.gif?itemid=13221416",
                   "https://media1.tenor.com/images/49a21e182fcdfb3e96cc9d9421f8ee3f/tenor.gif?itemid=3532079",
                   "https://media1.tenor.com/images/e9d7da26f8b2adbb8aa99cfd48c58c3e/tenor.gif?itemid=14721541",
                   "https://media1.tenor.com/images/f2805f274471676c96aff2bc9fbedd70/tenor.gif?itemid=7552077",
                   "https://media1.tenor.com/images/aeb42019b0409b98aed663f35b613828/tenor.gif?itemid=14108949",
                   "https://media1.tenor.com/images/09005550fb8642d13e544d2045a409c5/tenor.gif?itemid=7883854",
                   "https://media1.tenor.com/images/4ebdcd44de0042eb416345a50c3f80c7/tenor.gif?itemid=6155660",
                   "https://media1.tenor.com/images/1a73e11ad8afd9b13c7f9f9bb5c9a834/tenor.gif?itemid=13366388",
                   "https://media1.tenor.com/images/daffa3b7992a08767168614178cce7d6/tenor.gif?itemid=15249774",
                   "https://media1.tenor.com/images/f5df55943b64922b6b16aa63d43243a6/tenor.gif?itemid=9375012",
                   "https://cdn.discordapp.com/attachments/636850117995003906/637911833205932032/KHdSnNKk7.gif",
                   "https://cdn.discordapp.com/attachments/636850117995003906/637927282077466645/AL119.gif",
                   "https://cdn.discordapp.com/attachments/624296774747553808/639093222844399632/22.gif",
                   "https://cdn.discordapp.com/attachments/626362221957742602/639754461044015104/rkIK_u7Pb.gif",
                   "https://cdn.discordapp.com/attachments/621005423335702528/652823412518944791/3ZRdtZ3Ykjg.jpg"]
        description = f'**Обнимашки**\n{ctx.author.mention} ✧ {user.mention}'
        if message is not None:
            description = f'{description}\n{message}'
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=description)
        embed.set_author(name=self.client.user.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text='(ᴖ◡ᴖ)♪', icon_url=user.avatar.url)
        embed.set_image(random.choice(gifs))
        await ctx.send(embed=embed)

    @commands.command(aliases=['pat', 'погладить', 'гладить'])
    async def __pat(self, ctx, user: nextcord.Member=None, *, message: str = None):
        emoji = "<a:emoji_1:995590858734841938>"
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}hug <пользователь> [сообщение]')
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
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для использования команды, все команды эмоций стоят 5 {emoji}')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - 5, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        gifs = ["https://media1.tenor.com/images/f330c520a8dfa461130a799faca13c7e/tenor.gif?itemid=13911345",
                   "https://media1.tenor.com/images/da8f0e8dd1a7f7db5298bda9cc648a9a/tenor.gif?itemid=12018819",
                   "https://media1.tenor.com/images/daa885ec8a9cfa4107eb966df05ba260/tenor.gif?itemid=13792462",
                   "https://media1.tenor.com/images/c0bcaeaa785a6bdf1fae82ecac65d0cc/tenor.gif?itemid=7453915",
                   "https://media1.tenor.com/images/d9b480bcd392d05426ae6150e986bbf0/tenor.gif?itemid=9332926",
                   "https://media1.tenor.com/images/857aef7553857b812808a355f31bbd1f/tenor.gif?itemid=13576017",
                   "https://media1.tenor.com/images/c61cc63503c21c8e69452639f068ad7f/tenor.gif?itemid=15402635",
                   "https://media1.tenor.com/images/f5176d4c5cbb776e85af5dcc5eea59be/tenor.gif?itemid=5081286",
                   "https://media1.tenor.com/images/13f385a3442ac5b513a0fa8e8d805567/tenor.gif?itemid=13857199",
                   "https://media1.tenor.com/images/61187dd8c7985c443bf9cd39bc310c02/tenor.gif?itemid=12018805",
                   "https://media1.tenor.com/images/291ea37382e1d6cd33349c50a398b6b9/tenor.gif?itemid=10204936",
                   "https://media1.tenor.com/images/71e74263a48a6e9a2c53f3bc1439c3ac/tenor.gif?itemid=12434286",
                   "https://media1.tenor.com/images/266e5f9bcb3f3aa87ba39526ee202476/tenor.gif?itemid=5518317",
                   "https://media1.tenor.com/images/54722063c802bac30d928db3bf3cc3b4/tenor.gif?itemid=8841561",
                   "https://media1.tenor.com/images/bf646b7164b76efe82502993ee530c78/tenor.gif?itemid=7394758",
                   "https://media1.tenor.com/images/5466adf348239fba04c838639525c28a/tenor.gif?itemid=13284057",
                   "https://media1.tenor.com/images/005e8df693c0f59e442b0bf95c22d0f5/tenor.gif?itemid=10947495",
                   "https://media1.tenor.com/images/28f4f29de42f03f66fb17c5621e7bedf/tenor.gif?itemid=8659513",
                   "https://media1.tenor.com/images/64d45ee51ea8d55760c81a93353ffdb3/tenor.gif?itemid=11179299",
                   "https://media1.tenor.com/images/70960e87fb9454df6a1d15c96c9ad955/tenor.gif?itemid=10092582",
                   "https://media1.tenor.com/images/098a45951c569edc25ea744135f97ccf/tenor.gif?itemid=10895868",
                   "https://media1.tenor.com/images/ebd15359a3ae53d50a35055d79d325c9/tenor.gif?itemid=12018845",
                   "https://media1.tenor.com/images/2cf1704769d0227c69ebc4b6c85e274b/tenor.gif?itemid=10468802",
                   "https://media1.tenor.com/images/220babfd5f8b629cc16399497ed9dd96/tenor.gif?itemid=6130861"]
        description = f'**Поглаживание**\n{ctx.author.mention} ✧ {user.mention}'
        if message is not None:
            description = f'{description}\n{message}'
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=description)
        embed.set_author(name=self.client.user.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text='(ᴖ◡ᴖ)♪', icon_url=user.avatar.url)
        embed.set_image(random.choice(gifs))
        await ctx.send(embed=embed)

    @commands.command(aliases=['пять', 'датьпять', 'пятюня', 'five', 'highfive'])
    async def __highfive(self, ctx, user: nextcord.Member=None, *, message: str = None):
        emoji = "<a:emoji_1:995590858734841938>"
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}hug <пользователь> [сообщение]')
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
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для использования команды, все команды эмоций стоят 5 {emoji}')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - 5, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        gifs = ["https://c.tenor.com/JBBZ9mQntx8AAAAC/anime-high-five.gif",
                "https://c.tenor.com/Ajl4l3PWf8sAAAAC/high-five-anime.gif",
                "https://c.tenor.com/7KVY_BxUWbEAAAAC/high-five-anime.gif",
                "https://i.gifer.com/Pvwh.gif",
                "https://acegif.com/wp-content/gif/high-five-83.gif",
                "https://c.tenor.com/geq2owR6VPMAAAAM/ban-meliodas.gif",
                "http://25.media.tumblr.com/b0b33a1a6d1ea4dc25a5160f29d37b7b/tumblr_mt4r5oDhu81sqaw4ao1_400.gif"
               ]

        description = f'**Пятюня**\n{ctx.author.mention} ✧ {user.mention}'
        if message is not None:
            description = f'{description}\n{message}'
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=description)
        embed.set_author(name=self.client.user.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text='(*＾ω＾)人(＾ω＾*)', icon_url=user.avatar.url)
        embed.set_image(random.choice(gifs))
        await ctx.send(embed=embed)

    @commands.command(aliases=['ударить', 'punch'])
    async def __punch(self, ctx, user: nextcord.Member=None, *, message: str = None):
        emoji = "<a:emoji_1:995590858734841938>"
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}hug <пользователь> [сообщение]')
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
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для использования команды, все команды эмоций стоят 5 {emoji}')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - 5, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        gifs = ["https://media1.tenor.com/images/1c986c555ed0b645670596d978c88f6e/tenor.gif?itemid=13142581",
                     "https://media1.tenor.com/images/31686440e805309d34e94219e4bedac1/tenor.gif?itemid=4790446",
                     "https://media1.tenor.com/images/d7c30e46a937aaade4d7bc20eb09339b/tenor.gif?itemid=12003970",
                     "https://media1.tenor.com/images/c621075def6ca41785ef4aaea20cc3a2/tenor.gif?itemid=7679409",
                     "https://media1.tenor.com/images/6d77cf1fdaa2e7c6a32c370240a7b77c/tenor.gif?itemid=9523306",
                     "https://media1.tenor.com/images/965fabbfcdc09ee0eb4d697e25509f34/tenor.gif?itemid=7380310 ",
                     "https://media1.tenor.com/images/745d16a823805edbfe83aa9363c48a87/tenor.gif?itemid=12003981",
                     "https://media1.tenor.com/images/f03329d8877abfde62b1e056953724f3/tenor.gif?itemid=13785833",
                     "https://media1.tenor.com/images/7d43687195b86c8ce2411484eb1951fc/tenor.gif?itemid=7922533",
                     "https://media1.tenor.com/images/6afcfbc435b698fa5ceb2ff019718e6d/tenor.gif?itemid=10480971",
                     "https://media1.tenor.com/images/b82427b0507d43afb17a6c9ddddfa0a9/tenor.gif?itemid=4903584",
                     "https://media1.tenor.com/images/995c766275e66c3aa5efd55ab7d8f86a/tenor.gif?itemid=7885164",
                     "https://media1.tenor.com/images/cf467247b8755bcb943dc535ccfd1830/tenor.gif?itemid=9753290",
                     "https://media1.tenor.com/images/29ecede6bfa61d6a2fbfb4b63620cdb4/tenor.gif?itemid=14613404",
                     "https://media1.tenor.com/images/d37431cbc9bd68eca0d700c787bf33d0/tenor.gif?itemid=5521090",
                     "https://media1.tenor.com/images/d7d52d0592bbc77bd5c629c2132c1b33/tenor.gif?itemid=9409159",
                     "https://media1.tenor.com/images/313bb02914ddb9262511b790ef4d4c7b/tenor.gif?itemid=7922535",
                     "https://cdn.discordapp.com/attachments/624296774747553808/639094165732589580/30.gif",
                     "https://cdn.discordapp.com/attachments/624296774747553808/639094187903680522/31.gif",
                     "https://pa1.narvii.com/6329/041aa0724fb6e5dbf71681a80b86d5d1add8f8c8_hq.gif"]

        description = f'**Удар**\n{ctx.author.mention} ударяет {user.mention}'
        if message is not None:
            description = f'{description}\n{message}'
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=description)
        embed.set_author(name=self.client.user.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text='	٩(ఠ益ఠ)۶', icon_url=user.avatar.url)
        embed.set_image(random.choice(gifs))
        await ctx.send(embed=embed)

    @commands.command(aliases=['bite', 'кусь', 'укусить'])
    async def __bite(self, ctx, user: nextcord.Member=None, *, message: str = None):
        emoji = "<a:emoji_1:995590858734841938>"
        if user is None:
            embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
            embed.add_field(name='Ошибка', value=f'Правильное написание команды: '
                                                 f'{settings["PREFIX"]}hug <пользователь> [сообщение]')
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
            embed.add_field(name='Ошибка', value=f'У вас недостаточно {emoji} для использования команды, все команды эмоций стоят 5 {emoji}')
            cursor.close()
            db.close()
            return await ctx.send(embed=embed)
        sql = "UPDATE money SET money = ? WHERE user_id = ?"
        val = (balance - 5, ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        gifs = ["https://media1.tenor.com/images/d97e4bc853ed48bf83386664956d75ec/tenor.gif?itemid=10364764",
                    "https://media1.tenor.com/images/6b42070f19e228d7a4ed76d4b35672cd/tenor.gif?itemid=9051585",
                    "https://media1.tenor.com/images/418a2765b0bf54eb57bab3fde5d83a05/tenor.gif?itemid=12151511",
                    "https://media1.tenor.com/images/3baeaa0c5ae3a1a4ae9ac2780b2d965d/tenor.gif?itemid=13342683",
                    "https://media1.tenor.com/images/f3f456723f2f8735d118b43823c837f5/tenor.gif?itemid=14659250",
                    "https://media1.tenor.com/images/0d192209c8e9bcd9826af63ba72fc584/tenor.gif?itemid=15164408",
                    "https://media1.tenor.com/images/2adef5d4fba623aeb4c5b74879107b56/tenor.gif?itemid=5160295",
                    "https://media1.tenor.com/images/69546e40c361a59ce442c4d08e47bb05/tenor.gif?itemid=15157862",
                    "https://media1.tenor.com/images/f78e68053fcaf23a6ba7fbe6b0b6cff2/tenor.gif?itemid=10614631"]

        description = f'**Кусь**\n{ctx.author.mention} ✧ {user.mention}'
        if message is not None:
            description = f'{description}\n{message}'
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                               description=description)
        embed.set_author(name=self.client.user.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text='	(〃＞＿＜;〃', icon_url=user.avatar.url)
        embed.set_image(random.choice(gifs))
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Emotions(client))
