import discord

from pybot.database import update_client_lang, record_answer_event
from pybot.constants import SPONSOR_QUESTION_ANSWERS
from pybot.translation import (
    QUESTION_MODAL_TITLE,
    CORRECT_ANSWER_RESPONSE,
    WRONG_ANSWER_RESPONSE,
)


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
        await update_client_lang(uid=self.view.uid, lang=self.LANGUAGE_LABEL_TO_CODE_MAP[self.label])
        await interaction.response.send_message(content=self.resp_copy)


class LanguageSelectionView(discord.ui.View):
    def __init__(self, uid: str):
        super().__init__()
        self.uid = uid
        tw_copy = '你選擇了中文，之後所有對話將預設語言為中文顯示。'\
            '若是想更改語言，可隨時在對話框輸入指令 `!change_language` 修改。'
        en_copy = 'You\'ve choose English. All the following conversation will be shown in English.' \
            'If you want to change the language setting, type command `!change_language` anytime to modify.'
        self.add_item(LanguageButton(resp_copy=tw_copy, label='中文'))
        self.add_item(LanguageButton(resp_copy=en_copy, label='English'))


class SponsorshipQuestionModal(discord.ui.Modal):
    answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.short)

    def __init__(self, question_id: str, user: discord.Member, lang: str):
        super().__init__(title=QUESTION_MODAL_TITLE[lang])
        self.lang = lang
        self.qid = question_id
        self.user = user

    async def on_submit(self, interaction: discord.Interaction):
        user_ans = self.answer.value
        answer = SPONSOR_QUESTION_ANSWERS[self.qid]
        if user_ans == answer:
            resp_msg = CORRECT_ANSWER_RESPONSE[self.lang]
        else:
            resp_msg = WRONG_ANSWER_RESPONSE[self.lang]
        await interaction.response.send_message(resp_msg)
        await record_answer_event(self.qid, self.user.id, user_ans)


class SponsorshipQuestionDropdown(discord.ui.Select):
    def __init__(self, placeholder: str):
        # Four options, from A to D.
        options = [
            discord.SelectOption(label=qid)
            for qid in SPONSOR_QUESTION_ANSWERS
        ]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_qid = self.values[0]

        view: SponsorshipQuestionView = self.view
        await interaction.response.send_modal(
            SponsorshipQuestionModal(
                question_id=selected_qid,
                user=view.user,
                lang=view.lang,
            )
        )
        view.stop()


class SponsorshipQuestionView(discord.ui.View):
    def __init__(self, user: discord.Member, lang: str, timeout=30):
        super().__init__(timeout=timeout)

        placeholder = {
            'zh_TW': '選擇您要回答的問題',
            'EN': 'Please choose a question to answer'
        }[lang]

        self.add_item(SponsorshipQuestionDropdown(placeholder=placeholder,))
        self.lang = lang
        self.user = user
