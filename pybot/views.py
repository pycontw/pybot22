from typing import Dict

import discord

from pybot.database import (
    update_client_lang,
    record_answer_event,
    sync_update_client_lang,
    update_user_rewards,
)
from pybot.translation import (
    CORRECT_ANSWER_REWARD_MSG,
    QUESTION_MODAL_TITLE,
    CORRECT_ANSWER_RESPONSE,
    WRONG_ANSWER_RESPONSE,
)

from pybot.rank import rank_update

# CKP: short for Chan Kan Pon (Japanese of paper scissors stone game)
class CKPDropdown(discord.ui.Select):
    STR_TO_EMOJI_VALUE = {
        'Paper': ':hand_splayed:',
        'Scissors': ':v:',
        'Stone': ':fist:',
    }

    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Paper', emoji='🖐️'),
            discord.SelectOption(label='Scissors', emoji='✌️'),
            discord.SelectOption(label='Stone', emoji='✊'),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Paper seasor stone!', min_values=1, max_values=1, options=options)

        self.selection_status = {}

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: CKPDropdownView = self.view
        selected = self.values[0]
        emoji_str = self.STR_TO_EMOJI_VALUE[selected]
        user = interaction.user
        self.selection_status[user] = selected
        result_msg = view.check_winner(self.selection_status)
        if result_msg:
            view.stop()
            await interaction.response.send_message(content=result_msg)
        else:
            await interaction.response.send_message(
                content=f'Your choice is {emoji_str}. Waiting for others...',
                ephemeral=True
            )


class CKPDropdownView(discord.ui.View):
    def __init__(self, members, timeout=10):
        super().__init__(timeout=timeout)

        # Adds the dropdown to our view object.
        self.members = [m for m in members if not m.bot]
        self.timeout = timeout
        self.add_item(CKPDropdown())

    def check_winner(self, selection_status):
        if len(selection_status) < len(self.members):
            return None

        status = set(selection_status.values())
        if len(status) in (1, 3):
            return 'No results!'

        get_winners = lambda winner_status: [
            member
            for member, status in selection_status.items()
            if status == winner_status
        ]

        if status == {'Scissors', 'Stone'}:
            winners = get_winners('Stone')
        elif status == {'Scissors', 'Paper'}:
            winners = get_winners('Scissors')
        else:
            winners = get_winners('Paper')
        
        winner_msg = 'Winners are:' + ' '.join([w.mention for w in winners])
        return winner_msg


class LanguageButton(discord.ui.Button['Language']):
    LANGUAGE_LABEL_TO_CODE_MAP = {
        '中文': 'zh_TW',
        'English': 'EN',
    }

    def __init__(self, resp_copy: str, label: str = None):
        super().__init__(label=label)
        self.resp_copy = resp_copy

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: LanguageSelectionView = self.view
        view.stop()
        if view.sync_update:
            sync_update_client_lang(uid=self.view.uid, lang=self.LANGUAGE_LABEL_TO_CODE_MAP[self.label])
        else:
            await update_client_lang(uid=self.view.uid, lang=self.LANGUAGE_LABEL_TO_CODE_MAP[self.label])
        await interaction.response.send_message(content=self.resp_copy)


class LanguageSelectionView(discord.ui.View):
    def __init__(self, uid: str, sync_update: bool = False):
        super().__init__()
        self.uid = uid
        self.sync_update = sync_update
        tw_copy = '你選擇了中文，之後所有對話將預設語言為中文顯示。'\
            '若是想更改語言，可隨時在對話框輸入指令 `!change_language` 修改。'
        en_copy = 'You\'ve choose English. All the following conversation will be shown in English.' \
            'If you want to change the language setting, type command `!change_language` anytime to modify.'
        self.add_item(LanguageButton(resp_copy=tw_copy, label='中文'))
        self.add_item(LanguageButton(resp_copy=en_copy, label='English'))


class SponsorshipQuestionModal(discord.ui.Modal):
    answer_input = discord.ui.TextInput(label='Answer', style=discord.TextStyle.short)

    def __init__(
        self,
        q_info: dict,
        user: discord.Member,
        lang: str,
        trigger_view: 'SponsorshipQuestionView',
    ):
        super().__init__(title=QUESTION_MODAL_TITLE[lang])
        self.lang = lang
        self.q_info = q_info
        self.user = user
        self.trigger_view = trigger_view

    async def on_submit(self, interaction: discord.Interaction):
        user_ans = self.answer_input.value
        answer = self.q_info['answer']
        if user_ans == answer:
            resp_msg = CORRECT_ANSWER_RESPONSE[self.lang]
            if not self.trigger_view.already_answered:
                reward_msg = CORRECT_ANSWER_REWARD_MSG[self.lang].format(
                    coin=self.q_info['coin'],
                    star=self.q_info['star'],
                )
                resp_msg = f'{resp_msg}\n{reward_msg}'
            is_correct = True
            self.trigger_view.stop()
            await update_user_rewards(self.user.id, self.q_info['coin'], self.q_info['star'])
            # rank is in memory for light weight sync access in run time
            rank_update(self.user.id, self.q_info['coin'])
        else:
            resp_msg = WRONG_ANSWER_RESPONSE[self.lang]
            is_correct = False
        await interaction.response.send_message(resp_msg)
        await record_answer_event(self.q_info['qid'], self.user.id, user_ans, is_correct)


class SponsorshipQuestionView(discord.ui.View):
    def __init__(self, q_info: dict, user: discord.Member, lang: str, already_answered: bool):
        super().__init__()

        self.q_info = q_info
        self.lang = lang
        self.user = user
        self.answer_counts = 0

        self.already_answered = already_answered

    @discord.ui.button(label='開始回答 / Start Answering')
    async def trigger_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.already_answered:
            self.q_info['coin'] = 0
            self.q_info['star'] = 0
        else:
            self.q_info['coin'] = int(max(1, pow(0.5, self.answer_counts) * self.q_info['coin']))
            self.q_info['star'] = int(max(1, pow(0.5, self.answer_counts) * self.q_info['star']))
        self.answer_counts += 1
        await interaction.response.send_modal(
            SponsorshipQuestionModal(
                q_info=self.q_info,
                user=self.user, 
                lang=self.lang,
                trigger_view=self,
            )
        )


class GameDropdown(discord.ui.Select):
    def __init__(self, placeholder: str, q_options: Dict[str, str]):
        options = []
        for opt in q_options.values():
            options.append(discord.SelectOption(label=opt))

        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_ans = self.values[0]
        await self.view.check_ans_and_update_state(user_ans, interaction)


class GameSelectionView(discord.ui.View):
    def __init__(self, q_info: dict, user: discord.Member, lang: str, already_answered: bool):
        super().__init__()

        self.q_info = q_info
        self.lang = lang
        self.user = user
        self.answer_counts = 0

        self.already_answered = already_answered

        self.add_item(
            GameDropdown(
                placeholder='Click Me!',
                q_options=self.q_info['options']
            )
        )

    async def check_ans_and_update_state(self, user_ans: str, interaction: discord.Interaction):
        answer = self.q_info['answer']
        if user_ans == answer:
            # Calculate rewards
            reward_coin = int(max(1, self.q_info['coin'] * pow(0.5, self.answer_counts)))

            resp_msg = CORRECT_ANSWER_RESPONSE[self.lang]
            if not self.already_answered:
                reward_msg = CORRECT_ANSWER_REWARD_MSG[self.lang].format(
                    coin=reward_coin,
                    star=self.q_info['star'],
                )
                resp_msg = f'{resp_msg}\n{reward_msg}'
            is_correct = True
            self.stop()
            await update_user_rewards(interaction.user.id, reward_coin, self.q_info['star'])
        else:
            resp_msg = WRONG_ANSWER_RESPONSE[self.lang]
            is_correct = False
            self.answer_counts += 1
        await interaction.response.send_message(resp_msg)
        await record_answer_event(self.q_info['qid'], interaction.user.id, user_ans, is_correct)
