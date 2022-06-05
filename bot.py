import re
import toml
import random

import discord
from discord.ext import commands


credentials = toml.load(open('env.cred'))
TOKEN = credentials['DISCORD_TOKEN']
GUILD = credentials['DISCORD_GUILD']

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


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
    def __init__(self, members):
        super().__init__()

        # Adds the dropdown to our view object.
        self.members = [m for m in members if not m.bot]
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


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected!')


@bot.command(name='barcode')
async def barcode(ctx):
    if ctx.channel.id != 982232875715932162:
        # general channel
        return

    az_chrs = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    prefix = random.choices(az_chrs, k=2)
    prefix = ''.join(prefix)
    nums = random.choices(range(10), k=4)
    nums = ''.join([str(v) for v in nums])
    barcode = f'{prefix}-{nums}'

    await ctx.send(barcode)


@bot.command(name='redeem')
async def redeem(ctx, barcode: str):
    if ctx.channel.id != 982232875715932162:
        return
    if not re.match(r'[A-Z]{2}-\d{4}$', barcode):
        await ctx.send('Wrong barcode format.')
        return

    if hash(barcode) % 3 == 0:
        msg = 'Congratulations:crown:  You have won the prize.'
    else:
        msg = 'Ohoh...:poop: This barcode doesn\'t match any prize.'
    await ctx.send(msg)


@bot.command()
async def dice(ctx, upper: int = 6):
    print(ctx.channel.type == discord.ChannelType.private)
    await ctx.send(random.choice(range(upper)))


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


bot.run(TOKEN)

