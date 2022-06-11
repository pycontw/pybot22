import re
import random

import discord
from discord.ext import commands

from pybot import bot
from pybot.views import CKPDropdownView, LanguageSelectionView


@bot.command(name='change_language')
async def change_language(ctx: commands.Context):
    await ctx.send(
        '請選擇您的語言\n' \
        'Please select your language',
        view=LanguageSelectionView(uid=ctx.author.id)
    )


@bot.command(name='barcode')
async def barcode(ctx):
    if ctx.channel.id != 982232875715932162:
        # general channel
        return

    az_chrs = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    prefix = random.choices(az_chrs, k=2)
    prefix = ''.join(prefix)
    nums = random.choices(range(10), k=4)
    nums = ''.join([str(v) for v in nums])
    barcode = f'{prefix}-{nums}'

    await ctx.send(barcode)


@bot.command(name='redeem')
async def redeem(ctx, barcode: str):
    if ctx.channel.id != 982232875715932162:
        return
    if not re.match(r'[A-Z]{2}-\d{4}$', barcode):
        await ctx.send('Wrong barcode format.')
        return

    if hash(barcode) % 3 == 0:
        msg = 'Congratulations:crown:  You have won the prize.'
    else:
        msg = 'Ohoh...:poop: This barcode doesn\'t match any prize.'
    await ctx.send(msg)


@bot.command()
async def dice(ctx, upper: int = 6):
    print(ctx.channel.type == discord.ChannelType.private)
    await ctx.send(random.choice(range(upper)))


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