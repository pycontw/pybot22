import time
import asyncio
import threading

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


@task
async def update_leaderboard():
    channel_id = LEADER_BOARD_CHANNEL  # leaderboard channel
    channel = bot.get_channel(channel_id)
    msgs = [msg async for msg in channel.history(oldest_first=True)]
    if msgs:
        ranked_users = await query_user_rank_by_coin()
        messages = []
        for idx, user_d in enumerate(ranked_users):
            messages.append(f'#{idx+1} <@{user_d["uid"]}>: {user_d["coin"]}')

        top_one_user = bot.get_user(int(ranked_users[0]['uid']))
        avatar_url = top_one_user.display_avatar.url
        description = '\n'.join(messages)
        embed = discord.Embed(title='Rankings', description=description)
        embed.set_thumbnail(url=avatar_url)
        await msgs[0].reply(embed=embed)


schedule.every(5).minutes.do(update_leaderboard)
