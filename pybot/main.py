import os
import toml


from pybot import bot, test_bot
from pybot.commands import *
from pybot.schedule_events import run_schedule_events


def _parse_token():
    token = os.getenv('DISCORD_TOKEN')
    if token is None and os.path.exists('env.cred'):
        credentials = toml.load(open('env.cred'))
        token = credentials['DISCORD_TOKEN']
    return token


def main():
    try:
        #stop_run_continuously = run_schedule_events()
        bot.run('OTgyMjMzNTkyOTc5NjUyNjUw.GK2lOl.3GhwSrl_TH3mzwhvMhY18eDHEdmvwTPpWkc5fY')
    finally:
        #stop_run_continuously.set()
        pass


if __name__ == '__main__':
    main()
