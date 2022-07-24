import asyncio
from functools import partial
from typing import Callable

import discord
from discord.ext import commands
from discord.ext.commands import errors

from pybot.database import(
    check_client_has_lang,
    query_question,
    check_user_already_answered_qid,
)
from pybot.schemas import QuestionType
from pybot.translation import QUESTION_ANSWERED_REMINDER
from pybot.views import LanguageSelectionView, SponsorshipQuestionView
from pybot.database import cursor, record_command_event
from pybot.constants import INIT_GAME_MESSAGES


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


async def _init_lang(user_id: str, user_name: str, send_func: Callable):
    with cursor() as cur:
        cur.execute('''
            INSERT INTO profile (uid, name)
            VALUES (%(uid)s, %(name)s)
        ''', {'uid': user_id, 'name': user_name})

    await send_func(
        content='嗨嗨你好:wave: 請先選擇您的語言\n' \
            'Hi hi :wave: Please select your language first.',
        view=LanguageSelectionView(uid=user_id, sync_update=True),
    )
    
    idx = 50
    client_lang = None
    while idx > 0 and not client_lang:
        idx -=1
        client_lang = await check_client_has_lang(user_id)
        await asyncio.sleep(0.3)
    return client_lang


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

        client_lang = await check_client_has_lang(ctx.author.id)
        if ctx.invoked_with:
            if not client_lang:
                client_lang = await _init_lang(
                    ctx.author.id,
                    ctx.author.name,
                    partial(ctx.send, ephemeral=True),
                )

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
        else:
            await super().on_command_error(ctx, exception)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        # Bot itself
        if user.id == self.application_id:
            return

        # Check emoji in question pool
        if (
            (channel_id := reaction.message.channel.id) not in INIT_GAME_MESSAGES.keys()
            or reaction.emoji not in INIT_GAME_MESSAGES[channel_id]['emoji_to_qid']
        ):
            await reaction.remove(user)
            return

        # Init profile and language if first time
        client_lang = await check_client_has_lang(user.id)
        if not client_lang:
            client_lang = await _init_lang(user.id, user.name, user.send)

        # Get question info dict
        question_id = INIT_GAME_MESSAGES[channel_id]['emoji_to_qid'][reaction.emoji]
        q_info = await query_question(question_id, client_lang)

        # Response with different view according to the question type
        if q_info['q_type'] == QuestionType.TEXT:
            
            msg = q_info['description']
            if already_answered := await check_user_already_answered_qid(question_id, user.id):
                msg += QUESTION_ANSWERED_REMINDER[client_lang]
            await user.send(
                msg,
                view=SponsorshipQuestionView(
                    q_info=q_info,
                    user=user,
                    lang=client_lang,
                    already_answered=already_answered,
                )
            )
        elif q_info['q_type'] == QuestionType.SELECTION:
            ...
        elif q_info['q_type'] == QuestionType.QUESTIONARE:
            ...

        # Clear the reaction
        await reaction.remove(user)

def _get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    return intents


bot = PyBot22(command_prefix='!', intents=_get_intents())
