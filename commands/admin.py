import aiohttp
import nextcord
from nextcord.ext import commands
import asyncio
from config import settings


class AdministrationCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['announce', 'обьявление', 'аннаун', 'анаун', 'анаунс',
                               'аннаунс', 'онаунс', 'оннаунс', 'объяв', 'объявл', 'обьяв', 'обьявл', 'объявление'])
    @commands.has_permissions(administrator=True)
    async def __announce(self, ctx):
        title = 'титульник'
        description = 'описание, твой эмбед'
        embed_to_announce = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                           description=description, title=title)
        embed = nextcord.Embed(color=settings['defaultBotColor'])
        embed.add_field(name='Обозначение эмодзей', value='✅ - Отправить объявление в канал для объявлений\n'
                                                          '🔖 - установить титульник\n🎨 - установить поле автора\n'
                                                          '📕 - Установить описание\n1️⃣ - добавить 1 поле\n '
                                                          '2️⃣ - добавить 2 поле\n 3️⃣ - добавить 3 поле\n'
                                                          '🌆 - установить миниатюру\n🖼️ - установить изображение/gif\n'
                                                          '🏰 - установить подвал\n❌ - отмена команды')
        example_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at, description=
        'описание, самое большое поле, оно вмещает в себя целых 4096 символов, а ещё'
        ' не забываем, что поля можно свободно форматировать, к примеру: '
        '`оп`, **оп**, *оп*, __оп__, ***оп***, ``оп`` __**оп**__', title='титульник, до 256 символов, справо от '
                                                                         'титульника находится миниатюра, '
                                                                         'мини изображение, '
                                                                         'его можно не ставить, по умолчанию оно '
                                                                         'не установлено')
        example_embed.set_author(name='Этот эмбед - пример и объяснение полей.\nавторское поле, до 256 символов',
                                 url=self.client.user.avatar.url)
        example_embed.set_thumbnail(
            url='https://sun9-76.userapi.com/impf/6lUwW5CQFF8DKvQNctCQyMDOKxshlwid3tTt-g/gu4Moy9azWI.jpg?size=604x389&quality=96&sign=7d45e90d8ff9b0017932a8d5e9ca0581&type=album')
        example_embed.add_field(name='имя 1 поля до 256 символов', value='значение 1 поля до 1024 символов',
                                inline=False)
        example_embed.add_field(name='имя 2 поля до 256 символов', value='значение 2 поля до 1024 символов',
                                inline=False)
        example_embed.add_field(name='имя 3 поля до 256 символов', value='значение 3 поля '
                                                                         'до 1024 символов, под ним '
                                                                         'находится подвал '
                                                                         'и основное изображение', inline=False)
        example_embed.set_image(url='https://upload.wikimedia.org/wikipedia/ru/6/61/Rickrolling.gif')
        example_embed.set_footer(text='подвал до 2048 символов')
        await ctx.send(embed=example_embed)
        await ctx.send('твой эмбед сейчас выглядит так:')
        your_embed_msg = await ctx.send(embed=embed_to_announce)
        await ctx.send(embed=embed)
        menu_emojis = ['✅', '🔖', '🎨', '📕', '1️⃣', '2️⃣', '3️⃣', '🌆', '🖼️', '🏰', '❌']
        for e in menu_emojis:
            await your_embed_msg.add_reaction(e)

        def check(reaction, user):
            return (reaction.message.id == your_embed_msg.id) and (user.id == ctx.author.id) and (
                    str(reaction) in menu_emojis)

        try:
            reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=360)
        except asyncio.TimeoutError:
            await ctx.send("Timed out")
            return
        title = 'титульник'
        description = 'описание, твой эмбед'
        image_url = None
        thumbnail_url = None
        name_1 = None
        value_1 = None
        name_2 = None
        value_2 = None
        name_3 = None
        value = None
        footer = None
        author = None
        while str(reaction) != '✅' or '❌':
            if str(reaction) == '🔖':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка титульника',
                                     value=f'напишите сообщение для титульника ниже',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=360)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                title = reply.content
                embed_to_announce = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                                   description=f'{description}', title=f'{title}')
                if author is not None:
                    embed_to_announce.set_author(name=f'{author}')
                if footer is not None:
                    embed_to_announce.set_footer(text=f'{footer}')
                if image_url is not None:
                    embed_to_announce.set_image(url=image_url)
                if thumbnail_url is not None:
                    embed_to_announce.set_thumbnail(url=thumbnail_url)
                if name_1 is not None:
                    embed_to_announce.add_field(name=f'{name_1}', value=f'{value_1}', inline=False)
                if name_2 is not None:
                    embed_to_announce.add_field(name=f'{name_2}', value=f'{value_2}', inline=False)
                if name_3 is not None:
                    embed_to_announce.add_field(name=f'{name_3}', value=f'{value_3}', inline=False)
            if str(reaction) == '🎨':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка поля автора',
                                     value=f'напишите сообщение для поля автора ниже',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=360)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                author = reply.content
                embed_to_announce.set_author(name=f'{author}')
            if str(reaction) == '📕':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка описания',
                                     value=f'напишите сообщение для поля описания ниже',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=1080)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                description = reply.content
                embed_to_announce = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at,
                                                   description=f'{description}', title=f'{title}')
                if author is not None:
                    embed_to_announce.set_author(name=f'{author}')
                if footer is not None:
                    embed_to_announce.set_footer(text=f'{footer}')
                if image_url is not None:
                    embed_to_announce.set_image(url=image_url)
                if thumbnail_url is not None:
                    embed_to_announce.set_thumbnail(url=thumbnail_url)
                if name_1 is not None:
                    embed_to_announce.add_field(name=f'{name_1}', value=f'{value_1}', inline=False)
                if name_2 is not None:
                    embed_to_announce.add_field(name=f'{name_2}', value=f'{value_2}', inline=False)
                if name_3 is not None:
                    embed_to_announce.add_field(name=f'{name_3}', value=f'{value_3}', inline=False)
            if str(reaction) == '1️⃣':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка названия поля',
                                     value=f'напишите сообщение для НАЗВАНИЯ поля',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=360)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                name_1 = reply.content
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка ЗНАЧЕНИЯ поля',
                                     value=f'напишите сообщение для ЗНАЧЕНИЯ поля',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=1080)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                value_1 = reply.content
                embed_to_announce.add_field(name=f'{name_1}', value=f'{value_1}', inline=False)
            if str(reaction) == '2️⃣':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка названия поля',
                                     value=f'напишите сообщение для НАЗВАНИЯ поля',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=360)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                name_2 = reply.content
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка ЗНАЧЕНИЯ поля',
                                     value=f'напишите сообщение для ЗНАЧЕНИЯ поля',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=1080)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                value_2 = reply.content
                embed_to_announce.add_field(name=f'{name_2}', value=f'{value_2}', inline=False)
            if str(reaction) == '3️⃣':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка названия поля',
                                     value=f'напишите сообщение для НАЗВАНИЯ поля',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=360)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                name_3 = reply.content
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка ЗНАЧЕНИЯ поля',
                                     value=f'напишите сообщение для ЗНАЧЕНИЯ поля',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=1080)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                value_3 = reply.content
                embed_to_announce.add_field(name=f'{name_3}', value=f'{value_3}', inline=False)
            if str(reaction) == '🌆':
                try:
                    help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                    help_embed.add_field(name='Установка миниатюры',
                                         value=f'ОТПРАВЬТЕ ССЫЛКУ (URL) НА МИНИАТЮРУ',
                                         inline=False)
                    await ctx.send(embed=help_embed)

                    def check(author):
                        def inner_check(message):
                            return message.author == author

                        return inner_check

                    try:
                        reply = await self.client.wait_for('message', check=check(ctx.author), timeout=360)
                    except asyncio.TimeoutError:
                        await ctx.send("Timed out")
                        return
                    thumbnail_url = reply.content
                    embed_to_announce.set_thumbnail(url=thumbnail_url)
                except commands.CommandInvokeError(err):
                    await ctx.send(err)
            if str(reaction) == '🖼️':
                try:
                    help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                    help_embed.add_field(name='Установка миниатюры',
                                         value=f'ОТПРАВЬТЕ ССЫЛКУ (URL) НА ИЗОБРАЖЕНИЕ',
                                         inline=False)
                    await ctx.send(embed=help_embed)

                    def check(author):
                        def inner_check(message):
                            return message.author == author

                        return inner_check

                    try:
                        reply = await self.client.wait_for('message', check=check(ctx.author), timeout=360)
                    except asyncio.TimeoutError:
                        await ctx.send("Timed out")
                        return
                    image_url = reply.content
                    embed_to_announce.set_image(url=image_url)
                except commands.CommandInvokeError(err):
                    await ctx.send(err)
            if str(reaction) == '🏰':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Установка подвала',
                                     value=f'Напишите сообщение для подвала',
                                     inline=False)
                await ctx.send(embed=help_embed)

                def check(author):
                    def inner_check(message):
                        return message.author == author

                    return inner_check

                try:
                    reply = await self.client.wait_for('message', check=check(ctx.author), timeout=720)
                except asyncio.TimeoutError:
                    await ctx.send("Timed out")
                    return
                footer = reply.content
                embed_to_announce.set_footer(text=f'{footer}')
            if str(reaction) == '❌':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Отмена',
                                     value=f'Команда отменена',
                                     inline=False)
                return await ctx.send(embed=help_embed)
            if str(reaction) == '✅':
                help_embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
                help_embed.add_field(name='Ок',
                                     value=f'Сообщение отправлено в канал объявлений',
                                     inline=False)
                await ctx.send(embed=help_embed)
                announce_channel = self.client.get_channel(settings['announce_channel'])
                return await announce_channel.send(embed=embed_to_announce)
            await ctx.send('твой эмбед сейчас выглядит так:')
            your_embed_msg = await ctx.send(embed=embed_to_announce)
            await ctx.send(embed=embed)
            menu_emojis = ['✅', '🔖', '🎨', '📕', '1️⃣', '2️⃣', '3️⃣', '🌆', '🖼️', '🏰', '❌']
            for e in menu_emojis:
                await your_embed_msg.add_reaction(e)

            def check(reaction, user):
                return (reaction.message.id == your_embed_msg.id) and (user.id == ctx.author.id) and (
                        str(reaction) in menu_emojis)

            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=360)
            except asyncio.TimeoutError:
                await ctx.send("Timed out")
                return

    @__announce.error
    async def __announce_error_handler(self, ctx, error):
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        if isinstance(error, commands.CommandInvokeError):
            embed.add_field(name='Ошибка', value=f'Команда была прервана ошибкой класса InvokeError. '
                                                 f'Возникла неразрешимая ошибка:\n{error}')
            await ctx.send(embed=embed)




def setup(client):
    client.add_cog(AdministrationCommands(client))
