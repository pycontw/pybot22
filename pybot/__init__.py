
import discord
from discord.ext import commands

from pybot.utils import check_client_has_lang
from pybot.views import LanguageSelectionView
from pybot.database import cursor


class PyBot22Context(commands.Context):
    async def get_client_lang(self):
        lang = await check_client_has_lang(self.author.id)
        return lang if lang is not None else 'HAHAH'


async def _init_client(ctx):
    with cursor() as cur:
        cur.execute('''
            INSERT INTO profile (uid, name)
            VALUES (%(uid)s, %(name)s)
        ''', {'uid': ctx.author.id, 'name': ctx.author.name})

    await ctx.send(
        '嗨嗨你好:wave: 請先選擇您的語言\n' \
        'Hi hi :wave: Please select your language first.',
        view=LanguageSelectionView(uid=ctx.author.id)
    )


class PyBot22(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Register init_client to the command
        self._init_command = self.command(name='init_client')(_init_client)

    async def get_context(self, message, *, cls=PyBot22Context):
        return await super().get_context(message, cls=cls)

    async def on_message(self, message: discord.Message):
        # Overwrite the original function to allow trigger by another bot.
        ctx = await self.get_context(message)
        client_lang = await check_client_has_lang(ctx.author.id)
        if not client_lang:
            ctx.command = self._init_command
            await self.invoke(ctx)
        else:
            ctx.client_lang = client_lang
            await self.invoke(ctx)

    async def on_ready(self):
        print(f'{self.user.name} has connected!')


def _get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True


bot = PyBot22(command_prefix='!', intents=_get_intents())
