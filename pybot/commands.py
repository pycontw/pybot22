import random

import discord
from discord.ext import commands
from discord.errors import HTTPException

from pybot import bot
from pybot.settings import DEV_ENV, DEV_CHANNELS
from pybot.database import (
    query_user_has_stars,
    query_user_rank_by_coin,
    sync_query_init_messages,
    sync_check_user_is_staff,
    update_user_rewards
)
from pybot.translation import COMMAND_ONLY_AVAILABLE_PRIVATE_CHAT_MSG
from pybot.views import (
    CKPDropdownView,
    LanguageSelectionView,
)


async def check_is_private_chat_with_bot(ctx: commands.Context):
    if (
        isinstance(ctx.channel, discord.DMChannel)
        and ctx.channel.me.id == bot.application_id
    ):
        return True

    await ctx.send(COMMAND_ONLY_AVAILABLE_PRIVATE_CHAT_MSG[ctx.client_lang], ephemeral=True)
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
@commands.check(check_is_private_chat_with_bot)
async def confess_to(ctx: commands.Context, member: discord.Member, content: str):
    ctx.channel = bot.get_channel(982251980221214731)  # feature channel
    await ctx.send(member.mention + content)



@bot.command()
async def embed(ctx: commands.Context):
    ranked_users = await query_user_rank_by_coin()
    messages = []
    for idx, user_d in enumerate(ranked_users):
        messages.append(f'#{idx+1} <@{user_d["uid"]}>: {user_d["coin"]}')

    top_one_user = bot.get_user(int(ranked_users[0]['uid']))
    avatar_url = top_one_user.display_avatar.url
    description = '\n'.join(messages)
    embed = discord.Embed(title='Rankings', description=description)
    embed.set_thumbnail(url=avatar_url)

    ctx.channel = bot.get_channel(1006167895669223546)  # leaderboard channel
    await ctx.send(embed=embed)


## ----------------- Staff-only commands ----------------- ##

_check_is_staff = lambda ctx: sync_check_user_is_staff(ctx.author.id)

CHANNELS_TO_EXCLUDE_FROM_INIT = {
    1006167895669223546,  # leader-board
}


async def _init_leaderbaord_channel(ctx: commands.Context, clear_msgs: bool = False):
    channel  = bot.get_channel(1006167895669223546)
    msgs = [msg async for msg in channel.history(oldest_first=True, limit=10)]
    if clear_msgs:
        await channel.delete_messages(msgs)
        msgs = []

    if not msgs:
        ctx.channel = channel
        await ctx.send('大地遊戲的排行榜，依照每個人獲得的金幣進行排名，每隔 XX 分鐘更新一次')


@bot.command(hidden=True)
@commands.check(_check_is_staff)
async def init_leaderboard(ctx: commands.Context):
    await _init_leaderbaord_channel(ctx, clear_msgs=True)


@bot.command(hidden=True)
@commands.check(_check_is_staff)
async def init_game(ctx: commands.Context):
    init_messages = sync_query_init_messages()
    for target_channel, info_d in init_messages.items():
        if (
            (DEV_ENV and target_channel not in DEV_CHANNELS)
            or (not DEV_ENV and target_channel in DEV_CHANNELS)
            or (target_channel in CHANNELS_TO_EXCLUDE_FROM_INIT)
        ):
            continue

        welcome_msg = info_d['welcome_msg']
        channel = bot.get_channel(target_channel)

        # Delete all sent messages, or the restarted bot won't be able to receive reactions.
        await channel.delete_messages([msg async for msg in channel.history(oldest_first=True)])

        # Send messages to channel
        ctx.channel = channel
        new_msg = await ctx.send(welcome_msg)
        for emoji in info_d['emoji_to_qid']:
            if emoji is None:
                continue

            try:
                await new_msg.add_reaction(emoji)
            except HTTPException:
                guild = bot.get_guild(1000406827491676170)  # main server
                emoji = discord.utils.get(guild.emojis, name=emoji)
                await new_msg.add_reaction(emoji)

    await _init_leaderbaord_channel(ctx)


@bot.command(hidden=True)
@commands.check(_check_is_staff)
@commands.check(check_is_private_chat_with_bot)
async def staff_add_score(ctx: commands.Context, member: discord.Member, add_coin: int):
    await update_user_rewards(member.id, add_coin, 0)
    await ctx.send('Updated')
    await member.send(f'You have received {add_coin} coins~')


@bot.command(hidden=True)
@commands.check(_check_is_staff)
async def sync_channel_msg(ctx: commands.Context, channel_id: int):
    channel = bot.get_channel(channel_id)
    init_messages = sync_query_init_messages()
    info_d = init_messages[channel_id]
    msgs = [msg async for msg in channel.history(oldest_first=True)]
    if not msgs:
        return

    first_msg = msgs[0]
    await first_msg.clear_reactions()
    new_msg = await first_msg.edit(content=info_d['welcome_msg'])
    for emoji in info_d['emoji_to_qid']:
        if emoji is None:
            continue

        try:
            await new_msg.add_reaction(emoji)
        except HTTPException:
            guild = bot.get_guild(1000406827491676170)  # main server
            emoji = discord.utils.get(guild.emojis, name=emoji)
            await new_msg.add_reaction(emoji)


@bot.command(hidden=True)
@commands.check(_check_is_staff)
async def user_lotto(ctx: commands.Context, reward_n: int):
    # reward_n: numbers of rewards, the first 1 is the first reward, etc
    users = await query_user_has_stars(800, 5)

    flatten_users = []
    for user in users:
        flatten_users.extend(
            [(user['uid'], user['name'])] * user['star']
        )

    random.shuffle(flatten_users)

    chosen_users = set()
    for uid, user_name in flatten_users:
        chosen_users.add((uid, user_name))
        if len(chosen_users) == reward_n:
            break

    messages = []
    for idx, (uid, user_name) in enumerate(chosen_users):
        messages.append(f'#{idx+1} <@{uid}>')

    description = '\n'.join(messages)
    embed = discord.Embed(title='Sponsor Rewards', description=description)
    await ctx.send(embed=embed)


@bot.command(hiddent=True)
async def test(ctx: commands.Context):
    guild = bot.get_guild(1000406827491676170)
    for member in guild.members:
        print(member.name, member.roles)
