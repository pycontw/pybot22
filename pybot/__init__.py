
import discord
from discord.ext import commands
from discord.ext.commands import errors

from pybot.database import check_client_has_lang
from pybot.views import LanguageSelectionView
from pybot.database import cursor, record_command_event


class PyBot22Context(commands.Context):
    async def get_client_lang(self):
        lang = None #await check_client_has_lang(self.author.id)
        return lang if lang is not None else 'zh_TW'


async def _init_client(ctx):
    with cursor() as cur:
        cur.execute('''
            INSERT INTO profile (uid, name)
            VALUES (%(uid)s, %(name)s)
        ''', {'uid': ctx.author.id, 'name': ctx.author.name})

    await ctx.send(
        '嗨嗨你好:wave: 請先選擇您的語言\n' \
        'Hi hi :wave: Please select your language first.',
        view=LanguageSelectionView(uid=ctx.author.id),
        ephemeral=True,
    )


class PyBot22(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Register init_client to the command
        self._init_command = self.command(name='init_client', hidden=True)(_init_client)

    async def get_context(self, message, *, cls=PyBot22Context):
        return await super().get_context(message, cls=cls)

    async def on_message(self, message: discord.Message):
        # Overwrite the original function to allow trigger by another bot.
        ctx = await self.get_context(message)
        if ctx.author.id == self.application_id:
            # The bot itself
            return

        client_lang = 'zh_TW' #await check_client_has_lang(ctx.author.id)
        if ctx.invoked_with and not client_lang:
            ctx.command = self._init_command
            await self.invoke(ctx)
        else:
            ctx.client_lang = client_lang
            await self.invoke(ctx)
        await record_command_event(ctx.author.id, ctx.author.name, ctx.invoked_with)

    async def on_ready(self):
        print(f'{self.user.name} has connected!')

    async def on_command_error(self, ctx: commands.Context, exception: errors.CommandError):
        if isinstance(exception, errors.MissingRequiredArgument):
            await ctx.send(
                'Commands missing required arguments.'
                f'\nUsage: `{self.command_prefix}{ctx.command.name} {ctx.command.usage}`'
            )


def _get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    return intents


bot = PyBot22(command_prefix='!', intents=_get_intents())
