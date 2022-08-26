import toml
import time
import asyncio
import random
from typing import List, Optional

from discord.ext import commands
import discord

# Defines a custom button that contains the logic of the game.
# The ['TicTacToe'] bit is for type hinting purposes to tell your IDE or linter
# what the type of `self.view` is. It is not required.
class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


# This is our actual board View
class TicTacToe(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for y in range(4):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class TicTacToeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


class Dropdown(discord.ui.Select):
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
        await interaction.response.send_modal(AnswerTextInput())

    async def _callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: DropdownView = self.view
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


class DropdownView(discord.ui.View):
    def __init__(self, members=None):
        super().__init__()

        # Adds the dropdown to our view object.
        #self.members = [m for m in members if not m.bot]
        self.add_item(Dropdown())

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


class AnswerTextInput(discord.ui.Modal, title='Hahaha'):
    answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)


class TextInputView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(AnswerTextInput())


bot = TicTacToeBot()


@bot.command()
async def tic(ctx: commands.Context):
    """Starts a tic-tac-toe game with yourself."""
    
    await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe())


@bot.command()
async def chan_kan_pon(
    ctx: commands.Context,
    specified_members: commands.Greedy[discord.Member] = None
):
    if specified_members:
        members = specified_members
    elif isinstance(ctx.channel, discord.DMChannel):
        members = [ctx.author, ctx.channel.me]
    else:
        members = ctx.channel.recipients
    await ctx.send('Paper scissors stone!', view=DropdownView(members=members))


@bot.command()
async def answer(ctx):
    await ctx.send('hahaha', view=DropdownView())


## -------- Initialize Group Test -------- ##

class InitGroupButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        for children in view.children:
            children.style = discord.ButtonStyle.grey

        self.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=view)


class BaseInitGroupingView(discord.ui.View):
    description = ''
    lables = []

    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)
        for label in self.labels:
            self.add_item(InitGroupButton(label=label))


class InitGroupingQ1(BaseInitGroupingView):
    description = '哪個程式語言最讚?\nWhich programming language is the best?'
    labels = ['Java', 'Python', 'JavaScript']


class InitGroupingQ2(BaseInitGroupingView):
    description = '喜歡哪種食物?\nWhich food do you like more?'
    labels = ['披薩/Pizza', '小籠包/xiaolongbao (soup dumplings)', '壽司/Sushi']


class InitGroupingQ3(BaseInitGroupingView):
    description = '夢想成為...?\nDream to be a...?'
    labels = ['海賊王/Pirate king', '世界富豪/Magnate', '貓咪/Cat']


class InitGroupingQ4(BaseInitGroupingView):
    description = '最想擁有...?\nWish to have...?'
    labels = ['阿拉丁神燈/Aladdin\'s lamp', '妹妹/Younger sister', '貓咪/Cat']


class InitGroupingQ5(BaseInitGroupingView):
    description = '當程式寫不出來的時候你會...?\nWhat would do while you stuck in coding...?'
    labels = [
        '蹲在馬桶上思考 20 分鐘/Sit on the toilet and think for 20 minutes',
        '先睡一個小時的午覺/Take an 1-hour nap',
        '求神拜佛跪貓貓/Pray to God and cat',
    ]


async def _init_grouping(user_id: str, send_func):
    timeout_seconds = 180

    questions = [
        InitGroupingQ1,
        InitGroupingQ2,
        InitGroupingQ3,
        InitGroupingQ4,
        InitGroupingQ5,
    ]

    for grouping_inst in questions:
        await send_func(
            content=grouping_inst.description,
            view=grouping_inst(timeout=timeout_seconds),
        )

    group = random.choice(['Red', 'Yellow', 'Green'])
    await send_func(
	f'根據你的回答，你被分配到 **{view.group}** 組\n' \
	f'According to your answer, you are distributed to group **{view.group}**.\n'
	f'恭喜你完成了大地遊戲的註冊程序！接下來趕緊到我們的 Gather 場地來場台灣旅遊吧！\n'
	f'Game registration completed! The next step is landing our Gather space to start your journey to Taiwan virtually!\n'
	f'偷偷告訴你，沿著格子走可能會有意想不到的驚喜！\n'
	f'Find and walk along squares in the venue to get surprising!\n'
	f'趕快展開冒險吧 :partying_face:  盡可能的蒐集印章、拿金幣！\n'
	f'Collect Pawprint Stamps and coins as many as you can! Enjoy your journey!\n'
    )


@bot.command()
async def test(ctx: commands.Context):
    #await _init_grouping(ctx.author.id, ctx.send)
    await ctx.send(
        '填寫 Email 以收到大地遊戲得獎通知～\n' \
        'Fill your email for receiving game award notification~',
        view=EmailInputView()
    )


class EmailInputModal(discord.ui.Modal):
    email_input = discord.ui.TextInput(
        label='email',
        placeholder='e.g. pycon.2022@gmail.com',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        print(f'Received your email: {self.email_input.value}')


class EmailInputView(discord.ui.View):
    @discord.ui.button(label='開始填寫/Start filling')
    async def fill_in_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmailInputModal(title='Email Filling Form'))


TOKEN = 'OTgyMjMzNTkyOTc5NjUyNjUw.GK2lOl.3GhwSrl_TH3mzwhvMhY18eDHEdmvwTPpWkc5fY'
bot.run(TOKEN)
