import aiohttp
import nextcord
from nextcord.ext import commands, application_checks
from nextcord import Interaction
import asyncio
from config import settings


class EmbedModal(nextcord.ui.Modal):
    def __init__(self, client):
        super().__init__(
            "Делаем объявление UwU",
        )
        self.embedTitle = nextcord.ui.TextInput(label="Название, заголовок эмбеда", min_length=3, max_length=248,
                                                required=True, placeholder="Введите сюда заголовок для эмбеда")
        self.embedDescription = nextcord.ui.TextInput(label="Описание", min_length=5, max_length=1900,
                                                      required=True, placeholder="Введите сюда главный текст эмбеда",
                                                      style=nextcord.TextInputStyle.paragraph)

        self.embedURL = nextcord.ui.TextInput(label="URL главной картинки/гифки, не обязателен", min_length=5, max_length=250,
                                              required=False, placeholder="формат: "
                                                                         "https://www.example.com/image.png")
        self.embedURLthumbnail = nextcord.ui.TextInput(label="URL миниатюры, не обязателен", min_length=5, max_length=250,
                                              required=False, placeholder="формат: "
                                                                         "https://www.example.com/image.png")
        self.embedFooter = nextcord.ui.TextInput(label="текст футера, подвала, внизу, не обязателен", min_length=5, max_length=1900,
                                              required=False, placeholder="введите footer текст", style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.embedTitle)
        self.add_item(self.embedDescription)
        self.add_item(self.embedURL)
        self.add_item(self.embedURLthumbnail)
        self.add_item(self.embedFooter)
        self.client = client

    async def callback(self, interaction: Interaction) -> None:
        title = self.embedTitle.value
        description = self.embedDescription.value
        embed = nextcord.Embed(title=title, description=description,
                               color=settings['defaultBotColor'])
        if self.embedURL.value is not None:
            url = self.embedURL.value
            embed.set_image(url=url)
        if self.embedURLthumbnail.value is not None:
            thumbnail = self.embedURLthumbnail.value
            embed.set_thumbnail(url=thumbnail)
        if self.embedFooter.value is not None:
            footer = self.embedFooter.value
            embed.set_footer(text=footer)
        announce_channel = self.client.get_channel(settings['announce_channel'])
        await announce_channel.send(embed=embed)


class AdministrationCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="объявление", guild_ids=[924537075951366154], default_member_permissions=8,
                            description="позволяет создать обьявление, вызвает модал для создания эмбеда, доступно только администраторам")
    @application_checks.has_permissions(administrator=True)
    async def __announce(self, interaction: Interaction):
        modal = EmbedModal(self.client)
        await interaction.response.send_modal(modal)

    @__announce.error
    async def __announce_error_handler(self, ctx, error):
        embed = nextcord.Embed(color=settings['defaultBotColor'])
        if isinstance(error, commands.CommandInvokeError):
            embed.add_field(name='Ошибка', value=f'Команда была прервана ошибкой класса InvokeError. '
                                                 f'Возникла неразрешимая ошибка:\n{error}')
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(AdministrationCommands(client))
