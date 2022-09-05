from typing import Dict

import discord

from pybot.schemas import QuestionType
from pybot.database import (
    check_user_already_answered_qid,
    update_client_lang,
    record_answer_event,
    update_client_email,
    sync_update_client_lang,
    update_user_rewards,
)
from pybot.translation import (
    CORRECT_ANSWER_REWARD_MSG,
    QUESTION_MODAL_TITLE,
    CORRECT_ANSWER_RESPONSE,
    WRONG_ANSWER_RESPONSE,
)
from pybot.schemas import QuestionType
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
            '若是想更改語言，可回到 <#1000406828024336435> 按下 :abc: 進行更改～'
        en_copy = 'You\'ve choose English. All the following conversation will be shown in English.' \
            'If you want to change the language setting, you can go back to <#1000406828024336435>' \
            'and press :abc: to change~'
        self.add_item(LanguageButton(resp_copy=tw_copy, label='中文'))
        self.add_item(LanguageButton(resp_copy=en_copy, label='English'))


## -------- Booth game section -------- ##

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
        if user_ans == answer or self.q_info['q_type'] == QuestionType.QUESTIONARE:
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
    def __init__(self, placeholder: str, q_options: Dict[str, str], q_type: QuestionType):
        options = []
        for opt_key, opt_val in q_options.items():
            label = (
                opt_key
                if q_type == QuestionType.OPTION_ONLY
                else opt_val
            )
            options.append(discord.SelectOption(label=label))

        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_ans = self.values[0]
        await self.view.check_ans_and_update_state(user_ans, interaction)


class GameSelectionView(discord.ui.View):
    def __init__(self, q_info: dict, user: discord.Member, lang: str):
        super().__init__()

        self.q_info = q_info
        self.lang = lang
        self.user = user
        self.answer_counts = 0

        self.add_item(
            GameDropdown(
                placeholder='Click Me!',
                q_options=self.q_info['options'],
                q_type=self.q_info['q_type']
            )
        )

    async def check_ans_and_update_state(self, user_ans: str, interaction: discord.Interaction):
        if self.q_info['q_type'] == QuestionType.SELECTION:
            ans_opt = self.q_info['answer']
            answer = self.q_info['options'][ans_opt]
        else:
            answer = self.q_info['answer']

        # Check answer
        if (
            self.q_info['q_type'] == QuestionType.QUESTIONARE
            or user_ans == answer
        ):
            resp_msg = CORRECT_ANSWER_RESPONSE[self.lang]
            already_answered = await check_user_already_answered_qid(
                self.q_info['qid'],
                self.user.id,
            )
            if not already_answered:
                reward_coin = int(max(1, self.q_info['coin'] * pow(0.5, self.answer_counts)))
                reward_msg = CORRECT_ANSWER_REWARD_MSG[self.lang].format(
                    coin=reward_coin,
                    star=self.q_info['star'],
                )
                resp_msg = f'{resp_msg}\n{reward_msg}'
                await update_user_rewards(interaction.user.id, reward_coin, self.q_info['star'])
            is_correct = True
            self.stop()
        else:
            resp_msg = WRONG_ANSWER_RESPONSE[self.lang]
            is_correct = False
            self.answer_counts += 1

        # Dispatch message according to answer/question type.
        if (
            self.q_info['q_type'] == QuestionType.QUESTIONARE
            and user_ans in ('其他', 'Others')
        ):
            await interaction.response.send_modal(
                SponsorshipQuestionModal(
                    q_info=self.q_info,
                    user=self.user, 
                    lang=self.lang,
                    trigger_view=self,
                )
            )
        else:
            await interaction.response.send_message(resp_msg)
        await record_answer_event(self.q_info['qid'], interaction.user.id, user_ans, is_correct)


## -------- Question views when initialization -------- ##

class InitGroupButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        for children in view.children:
            children.style = discord.ButtonStyle.grey

        self.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=view)
        await record_answer_event(view.qid, interaction.user.id, self.label, True)
        if view.next_view:
            if view.next_view.is_final:
                from pybot import bot  # avoid circular import
                guild = bot.get_guild(1000406827491676170)
                role = guild.get_role(1012006097919430746)
                member = guild.get_member(interaction.user.id)
                await member.add_roles(role)
                await interaction.followup.send(
                    f'根據你的回答，你被分配到 **{view.group}** 組\n' \
                    f'According to your answer, you are distributed to group **{view.group}**.\n'
                    '恭喜你完成了大地遊戲的註冊程序！接下來趕緊到我們的 Gather 場地來場台灣旅遊吧！\n'
                    'Game registration completed! The next step is landing our Gather space to start your journey to Taiwan virtually!\n'
                    '偷偷告訴你，沿著格子走可能會有意想不到的驚喜！\n'
                    'Find and walk along squares in the venue to get surprising!\n'
                    '趕快展開冒險吧 :partying_face:  盡可能的蒐集印章、拿金幣！\n'
                    'Collect Pawprint Stamps and coins as many as you can! Enjoy your journey!\n'
                    'Space A : https://app.gather.town/app/nGOG11wkRybqeJff/PyCon%20APAC%202022%20-%20Space%20A\n'
                    'Space B : https://app.gather.town/app/NiHQgKoi7Bj0slmj/PyCon%20APAC%202022%20-%20Space%20B\n'
                )
            else:
                await interaction.followup.send(
                    content=view.next_view.description,
                    view=view.next_view(group=view.group, timeout=view.timeout),
                )


class BaseInitGroupingView(discord.ui.View):
    qid = ''
    description = ''
    lables = []
    next_view = None
    is_final = False

    def __init__(self, group: str, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.group = group
        for label in self.labels:
            self.add_item(InitGroupButton(label=label))


class InitGroupingFinish(BaseInitGroupingView):
    qid = 'init_q6'
    is_final = True


class InitGroupingQ5(BaseInitGroupingView):
    qid = 'init_q5'
    description = '5/5\n當程式寫不出來的時候你會...?\nWhat would do while you stuck in coding...?'
    labels = [
        '蹲在馬桶上思考 20 分鐘/Sit on the toilet and think for 20 minutes',
        '先睡一個小時的午覺/Take an 1-hour nap',
        '求神拜佛跪貓貓/Pray to God and cat',
    ]
    next_view = InitGroupingFinish


class InitGroupingQ4(BaseInitGroupingView):
    qid = 'init_q4'
    description = '4/5\n最想擁有...?\nWish to have...?'
    labels = ['阿拉丁神燈/Aladdin\'s lamp', '妹妹/Younger sister', '貓咪/Cat']
    next_view = InitGroupingQ5


class InitGroupingQ3(BaseInitGroupingView):
    qid = 'init_q3'
    description = '3/5\n夢想成為...?\nDream to be a...?'
    labels = ['海賊王/Pirate king', '世界富豪/Magnate', '貓咪/Cat']
    next_view = InitGroupingQ4


class InitGroupingQ2(BaseInitGroupingView):
    qid = 'init_q2'
    description = '2/5\n喜歡哪種食物?\nWhich food do you like more?'
    labels = ['披薩/Pizza', '小籠包/xiaolongbao (soup dumplings)', '壽司/Sushi']
    next_view = InitGroupingQ3


class InitGroupingQ1(BaseInitGroupingView):
    qid = 'init_q1'
    description = '1/5\n哪個程式語言最讚?\nWhich programming language is the best?'
    labels = ['Java', 'Python', 'JavaScript']
    next_view = InitGroupingQ2


class EmailInputModal(discord.ui.Modal):
    email_input = discord.ui.TextInput(
        label='email',
        placeholder='e.g. pycon.2022@gmail.com',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await update_client_email(interaction.user.id, self.email_input.value)
        await interaction.response.send_message(f'Received your email: {self.email_input.value}')


class EmailInputView(discord.ui.View):
    @discord.ui.button(label='開始填寫/Start filling')
    async def fill_in_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmailInputModal(title='Email Filling Form'))


## -------- Admin commands -------- ##
