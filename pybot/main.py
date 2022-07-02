import os
import toml

from pybot import bot
from pybot.commands import *


def _parse_token():
    token = os.getenv('DISCORD_TOKEN')
    if token is None and os.path.exists('env.cred'):
        credentials = toml.load(open('env.cred'))
        token = credentials['DISCORD_TOKEN']
    return token


def main():
    # bot.run(_parse_token())
    bot.run('OTgyMjMzNTkyOTc5NjUyNjUw.GK2lOl.3GhwSrl_TH3mzwhvMhY18eDHEdmvwTPpWkc5fY')


if __name__ == '__main__':
    main()
