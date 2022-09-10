import os

from pybot import bot
from pybot.commands import *
from pybot.schedule_events import run_schedule_events


TOKEN = os.getenv('DISCORD_TOKEN')


def main():
    try:
        #stop_run_continuously = run_schedule_events()
        #bot.run(TOKEN)
        bot.run('MTAxNzY4ODM0NzY0MjE4MzY5MA.GTO_U0.CC3TOAwidQYCGaYdUU0gbFSuzKcI9U-mkH_pS0')
    finally:
        #stop_run_continuously.set()
        ...


if __name__ == '__main__':
    main()
