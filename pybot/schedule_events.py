import time
import asyncio
import threading

import schedule

from pybot import bot


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
async def test():
    channel_id = 997710004087967827
    channel = bot.get_channel(channel_id)
    first_msg = [msg async for msg in channel.history(oldest_first=True)][0]
    await first_msg.reply('⭐')


schedule.every(3).seconds.do(test)
