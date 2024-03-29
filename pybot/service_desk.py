
import discord

from pybot.views import LanguageSelectionView
from pybot.schemas import ServiceType
from pybot.database import query_user_rewards
from pybot.translation import CHECK_COINS_RESP


async def command_distributor(q_info: dict, user: discord.Member):
    desc = q_info['description']
    if desc == ServiceType.INIT_PROFILE:
        # Do nothing. Any first reaction to the bot will trigger the initialization
        # process.
        pass
    elif desc == ServiceType.CHANGE_LANGUAGE:
        await user.send(
            '請選擇您的語言\n' \
            'Please select your language',
            view=LanguageSelectionView(uid=user.id, sync_update=True),
        )
    elif desc == ServiceType.CHECK_COINS:
        rewards = await query_user_rewards(user.id)
        resp = CHECK_COINS_RESP[q_info['lang']].format(
            coins=rewards['coin'],
            stars=rewards['star'],
        )
        await user.send(resp)
    return None
