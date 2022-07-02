import re
import random

import discord
from discord.ext import commands

from pybot import bot
from pybot.constants import SPONSOR_QUESTION_ANSWERS
from pybot.translation import (
    COMMAND_ONLY_AVAILABLE_PRIVATE_CHAT_MSG,
    QUESTION_ID_NOT_FOUND_MSG,
)
from pybot.views import (
    CKPDropdownView,
    LanguageSelectionView,
    SponsorshipQuestionView,
)


def check_is_private_chat_with_bot(channel: discord.abc.Messageable):
    if (
        isinstance(channel, discord.DMChannel)
        and channel.me.id == bot.application_id
    ):
        return True
    return False


@bot.command(name='change_language')
async def change_language(ctx: commands.Context):
    await ctx.send(
        '請選擇您的語言\n' \
        'Please select your language',
        view=LanguageSelectionView(uid=ctx.author.id),
        ephemeral=True,
    )


@bot.command()
async def answer(ctx: commands.Context):
    if not check_is_private_chat_with_bot(ctx.channel):
        await ctx.send(COMMAND_ONLY_AVAILABLE_PRIVATE_CHAT_MSG[ctx.client_lang])
        return

    await ctx.send(
        view=SponsorshipQuestionView(lang=ctx.client_lang),
        ephemeral=True,
    )


@bot.command()
async def dice(ctx, upper: int = 6):
    print(ctx.channel.type == discord.ChannelType.private)
    await ctx.send(random.randint(1, upper))


@bot.command()
async def chan_kan_pon(
    ctx: commands.Context,
    specified_members: commands.Greedy[discord.Member] = None
):
    if specified_members:
        members = specified_members
    elif isinstance(ctx.channel, discord.DMChannel):
        members = [ctx.author, ctx.channel.me]
    elif hasattr(ctx.channel, 'recipients'):
        members = ctx.channel.recipients
    else:
        members = [
            member
            async for member in ctx.guild.fetch_members()
        ]
    await ctx.send(
        'Paper scissors stone! Please submit in 10 seconds.',
        view=CKPDropdownView(members=members, timeout=10)
    )


@bot.command(
    help='Too shy to express your love? Let PyBot helps you!',
    usage='"<user_name>" "<your_confession_message>"',
)
async def confess_to(ctx: commands.Context, member: discord.Member, content: str):
    if not check_is_private_chat_with_bot(ctx.channel):
        await ctx.send(COMMAND_ONLY_AVAILABLE_PRIVATE_CHAT_MSG[ctx.client_lang])
        return

    ctx.channel = bot.get_channel(982251980221214731)  # feature channel
    await ctx.send(member.mention + content)
