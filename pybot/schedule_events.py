import time
import asyncio
import threading
from datetime import datetime, timedelta, timezone

import discord
import schedule

from pybot import bot
from pybot.database import query_user_rank_by_coin
from pybot.settings import LEADER_BOARD_CHANNEL


def run_schedule_events(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                if bot.is_ready():
                    schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def task(func):
    def wrapper():
        if asyncio.iscoroutinefunction(func):
            return asyncio.run_coroutine_threadsafe(func(), bot.loop)
        return func()
    return wrapper



TPE_TIMEZONE = timezone(timedelta(hours=8))
UPDATE_TIME_RANGE = {
    2: (
        datetime(2022, 8, 31, 23, 26, tzinfo=TPE_TIMEZONE),
        datetime(2022, 8, 31, 23, 30, tzinfo=TPE_TIMEZONE)
    ),
    5: (
        datetime(2022, 9, 3, 8, 20, tzinfo=TPE_TIMEZONE),
        datetime(2022, 9, 3, 20, 10, tzinfo=TPE_TIMEZONE)
    ),
    6: (
        datetime(2022, 9, 4, 9, 20, tzinfo=TPE_TIMEZONE),
        datetime(2022, 9, 4, 16, 00, tzinfo=TPE_TIMEZONE)
    )
}


@task
async def update_leaderboard():
    today = datetime.now(TPE_TIMEZONE).weekday()
    start, end = UPDATE_TIME_RANGE.get(today, (None, None))
    now = datetime.now(TPE_TIMEZONE)
    # if (
    #     now < datetime(2022, 8, 1, 1, 0, tzinfo=TPE_TIMEZONE)
    #     or not (
    #         start is not None
    #         and end is not None
    #         and (start <= now <= end)
    #     )
    # ):
    #     return

    channel_id = LEADER_BOARD_CHANNEL  # leaderboard channel
    channel = bot.get_channel(channel_id)
    msgs = [msg async for msg in channel.history(oldest_first=True)]

    if msgs and (ranked_users := await query_user_rank_by_coin()):
        messages = []
        for idx, user_d in enumerate(ranked_users):
            messages.append(f'#{idx+1} <@{user_d["uid"]}>: {user_d["coin"]}')

        top_one_user = bot.get_user(int(ranked_users[0]['uid']))
        avatar_url = top_one_user.display_avatar.url
        description = '\n'.join(messages)
        embed = discord.Embed(title='<:cat_coin:1013823752418623509> Rankings', description=description)
        embed.set_thumbnail(url=avatar_url)
        await msgs[0].reply(embed=embed)


schedule.every(5).minutes.do(update_leaderboard)
