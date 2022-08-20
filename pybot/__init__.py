import time
import asyncio
import random
from functools import partial
from typing import Callable

import discord
from discord.ext import commands
from discord.ext.commands import errors

from pybot.database import(
    check_client_has_lang,
    query_question,
    check_user_already_answered_qid,
    record_reaction_event,
)
from pybot.schemas import QuestionType
from pybot.translation import QUESTION_ANSWERED_REMINDER
from pybot.views import (
    LanguageSelectionView,
    SponsorshipQuestionView,
    GameSelectionView,
    GROUPING_QS,
    EmailInputView,
)
from pybot.database import (
    cursor,
    record_command_event,
    sync_query_init_messages,
    query_next_questionnaire,
)
from pybot.rank import rank_init


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


async def _init_grouping(user_id: str, send_func) -> str:
    timeout_seconds = 180

    await send_func(
        '在正式開始前先來做個小測驗吧～\n' \
        'Before starting, let\'t have a small test first~'
    )

    for grouping_inst in GROUPING_QS:
        await send_func(
            content=grouping_inst.description,
            view=grouping_inst(timeout=timeout_seconds),
        )

    group = random.choice(['Red', 'Yellow', 'Blue'])
    await send_func(
        f'根據你的回答，你被分配到 **{group}** 組\n' \
        f'According to your answer, you are distributed to group **{group}**.'
    )
    return group


async def _init_lang_and_grouping(user_id: str, user_name: str, send_func: Callable):
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
    await send_func(
        '填寫 Email 以收到大地遊戲得獎通知～\n' \
        'Fill your email for receiving game award notification~',
        view=EmailInputView(),
    )
    group = await _init_grouping(user_id, send_func)
    with cursor() as cur:
        params = {'group': group, 'uid': user_id}
        cur.execute('UPDATE profile SET team=%(group)s WHERE uid=%(uid)s', params)

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

        rank_init()

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
                client_lang = await _init_lang_and_grouping(
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
        elif isinstance(exception, errors.CheckFailure):
            print(f'Check failure: {str(exception)}')
        else:
            await super().on_command_error(ctx, exception)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        init_message = sync_query_init_messages()

        # Bot itself
        if (
            user.id == self.application_id
            or (channel_id := reaction.message.channel.id) not in init_message
        ):
            return

        if isinstance(reaction.emoji, str):
            # Normal emoji
            emoji = reaction.emoji
        else:
            # Custom emoji, which is type of discord.emoji.Emoji
            emoji = reaction.emoji.name

        print(reaction.emoji)

        # Check emoji in question pool
        if emoji not in init_message[channel_id]['emoji_to_qid']:
            await reaction.remove(user)
            return

        # Init profile and language if first time
        client_lang = await check_client_has_lang(user.id)
        if not client_lang:
            client_lang = await _init_lang_and_grouping(user.id, user.name, user.send)

        # Get question info dict
        question_id = init_message[channel_id]['emoji_to_qid'][emoji]
        q_info = await query_question(question_id, client_lang)

        if q_info['q_type'] == QuestionType.QUESTIONARE:   
            q_info = await query_next_questionnaire(str(user.id), client_lang)
            if not q_info:
                await user.send('You have already answered all questionnaires~')
                return
        elif q_info['q_type'] == QuestionType.SERVICE:
            # Actually not a question, but command utility.
            pass

        msg = q_info['description']
        if (
            q_info['q_type'] != QuestionType.QUESTIONARE
            and (already_answered := await check_user_already_answered_qid(question_id, user.id))
        ):
            msg += QUESTION_ANSWERED_REMINDER[client_lang]

        # Response with different view according to the question type
        if q_info['q_type'] == QuestionType.PURE_MESSAGE:
            await user.send(q_info['description'])
        elif q_info['q_type'] == QuestionType.TEXT:
            await user.send(
                msg,
                view=SponsorshipQuestionView(
                    q_info=q_info,
                    user=user,
                    lang=client_lang,
                    already_answered=already_answered,
                )
            )
        elif q_info['q_type'] in (QuestionType.SELECTION, QuestionType.OPTION_ONLY):
            await user.send(
                msg,
                view=GameSelectionView(
                    q_info=q_info,
                    user=user,
                    lang=client_lang,
                    already_answered=already_answered,
                )
            )
        elif q_info['q_type'] == QuestionType.QUESTIONARE:
            await user.send(
                msg,
                view=GameSelectionView(
                    q_info=q_info,
                    user=user,
                    lang=client_lang,
                    already_answered=False,
                )
            )

        # Clear the reaction
        await reaction.remove(user)
        await record_reaction_event(question_id, user.id, channel_id, reaction.message.channel.name)


def _get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    return intents


bot = PyBot22(command_prefix='!', intents=_get_intents())
