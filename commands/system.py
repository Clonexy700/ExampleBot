import nextcord
from nextcord.ext import commands
import os
from config import settings


class System(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['ping'])
    async def __ping(self, ctx):
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar.url)
        embed.add_field(name='Задержка', value=f'Пинг: {round(self.client.latency * 1000)} мс')
        embed.set_footer(text=f'{ctx.author.name}', icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @commands.command(aliases=['help', 'хелп'])
    async def __help(self, ctx):
        embed = nextcord.Embed(color=settings['defaultBotColor'], timestamp=ctx.message.created_at)
        embed.set_author(name=f'{self.client.user.name}', icon_url=self.client.user.avatar.url)
        embed.add_field(name='Экономика', value=f"`{settings['PREFIX']}баланс/balance/bal/$ <@>`"
                                                f"\n`{settings['PREFIX']}timely/еж/награда`"
                                                f"\n`{settings['PREFIX']}mtop/mld/мтоп`"
                                                f"\n`{settings['PREFIX']}send/give/дать`", inline=False)
        embed.add_field(name='Информация, профили', value=f"`{settings['PREFIX']}me/profile/профиль/я <@>`", inline=False)
        embed.add_field(name='Уровни, лвла', value=f"`{settings['PREFIX']}lvl/левел/лвл/левел <@>`"
                                                   f"\n`{settings['PREFIX']}ltop/lld/ld/лтоп`", inline=False)
        embed.add_field(name='Свадьбы', value=f"`{settings['PREFIX']}marry/свадьба <@>`"
                                              f"\n`{settings['PREFIX']}divorce/развод`"
                                              f"\n`{settings['PREFIX']}lp/lprofile/loveprofile`", inline=False)
        embed.add_field(name='Модерация', value=f"`{settings['PREFIX']}m/mute/мут <@> <время> <причина>`"
                                                f"\n`{settings['PREFIX']}um/unmute/размут <@>`"
                                                f"\n`{settings['PREFIX']}w/warn/варн/пред <@> <время> <причина>`", inline=False)
        embed.add_field(name='Системное', value=f"`{settings['PREFIX']}ping/пинг`", inline=False)
        embed.add_field(name='Войсы', value=f"`{settings['PREFIX']}vonline/online`"
                                            f"\n`{settings['PREFIX']}vtop/vld/втоп`", inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(System(client))
