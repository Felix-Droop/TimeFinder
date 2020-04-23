import os
from dotenv import load_dotenv

import discord
from discord.ext import tasks, commands

from datetime import datetime
from datetime import time
import intervals as I

import ast

# to be eliminated when discord.py version 1.4 is available
saving_loop_running = False

time_intervals = {}

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

def initialize_time_intervals():
    try:
        with open('TimeFinder.data', 'r') as file:
            raw_string = file.read()
        
        string_dict = ast.literal_eval(raw_string)

        converter = lambda s: datetime.strptime(s, '%H:%M').time()

        for name, string_interval in string_dict.items():
            time_intervals[name] = I.from_string(string_interval, conv = converter)

    except:
        guild = discord.utils.get(bot.guilds, name=GUILD)

        for member in guild.members:
            if not member.bot:
                time_intervals[member.display_name] = I.empty()

def save_time_intervals():
    store_dict = {}

    for name, interval in time_intervals.items():
        store_dict[name] = I.to_string(interval, conv = lambda v: v.strftime('%H:%M'))

    with open('TimeFinder.data', 'w+') as file:
        file.write(str(store_dict))

def time_interval_to_str(interval):
    params = {
        'disj': ', ',
        'sep': ' - ',
        'left_closed': '',
        'right_closed': '',
        'left_open': '',
        'right_open': '',
        'conv': lambda s: s.strftime('%H:%M')
    }

    return I.to_string(interval, **params)

def all_intervals_md_format(title):
    string = '```' + title + ':\n'

    for name, interval in time_intervals.items():
        string += f'\t{name}: {time_interval_to_str(interval)}\n'
    
    return string + '```'

async def send_state_in_discord(title):
    guild = discord.utils.get(bot.guilds, name = GUILD)
    
    role = discord.utils.get(guild.roles, name = 'Bot Admin')

    for member in role.members:
        if member.dm_channel is None:
            await member.create_dm()

        await member.dm_channel.send(all_intervals_md_format(title))

@tasks.loop(hours = 1)
async def keep_saving():
    save_time_intervals()

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    initialize_time_intervals()

    global saving_loop_running
    if not saving_loop_running:
        keep_saving.start()
        saving_loop_running = True

    await send_state_in_discord('ready')

@bot.command(name = 'add', help = 'Adds a time interval, format: XX:XX XX:XX')
async def add(ctx, time_begin, time_end):
    name = ctx.author.display_name

    try:
        time_interval = I.open(
            datetime.strptime(time_begin, '%H:%M').time(),
            datetime.strptime(time_end, '%H:%M').time()
            )

    except:
        await ctx.send('Incorrect time format.')
    
    
    if time_interval.is_empty():
        await ctx.send('Your time interval is empty. Did you swap the begin and end time?')

    else:
        try: 
            time_intervals[name] |= time_interval

            await ctx.send(f'Added {time_interval_to_str(time_interval)} for {name}.')
        
        except:
            await ctx.send('Insertion failed. Try full reseting if possible.')

    await send_state_in_discord(f'add ({name})')

@bot.command(name = 'when', help = 'Calculates the common time of all members')
async def when(ctx):
    common_interval = I.closed(time(0, 1), time(23, 59))

    for member_interval in time_intervals.values():
        common_interval &= member_interval

    if common_interval.is_empty():
        await ctx.send('There is no common time.')
    else:
        await ctx.send(time_interval_to_str(common_interval))

    await send_state_in_discord(f'when ({ctx.author.display_name})')

@bot.command(name = 'show', help = 'Prints all currently registered time intervals')
async def show(ctx):
    await ctx.send(all_intervals_md_format('Time intervals'))

    await send_state_in_discord(f'show ({ctx.author.name})')

@commands.has_role('Bot Admin')
@bot.command(name = 'reset_all', help = 'Resets the timetable for everyone to the last saved state, only "Bot Admin" can do this')
async def reset_all(ctx):
    time_intervals.clear()

    initialize_time_intervals()

    await ctx.send('Reseted the timetable.')

    await send_state_in_discord(f'reset_all ({ctx.author.display_name})')

@commands.has_role('Bot Admin')
@bot.command(name = 'empty', help = 'Empties the timetable for everyone, only "Bot Admin" can do this')
async def empty(ctx):
    time_intervals.clear()

    guild = discord.utils.get(bot.guilds, name=GUILD)

    for member in guild.members:
        if not member.bot:
            time_intervals[member.display_name] = I.empty()

    await ctx.send('Emptied the timetable.')

    await send_state_in_discord(f'empty ({ctx.author.display_name})')

@bot.command(name = 'empty_me', help = 'Empties the timetable for the calling user')
async def empty_me(ctx):
    name = ctx.author.display_name

    time_intervals[name] = I.empty()

    await ctx.send(f'Emptied the timetable for {name}.')

    await send_state_in_discord(f'reset_me ({name})')

@commands.has_role('Bot Admin')
@bot.command(name = 'disconnect', help = 'Disconnects the bot and saves the timetable')
async def disconnect(ctx):
    await ctx.send('Goodbye.')

    await send_state_in_discord('disconnect')

    await bot.logout()

@bot.event
async def on_member_join(member):
    if not member.bot:
        time_intervals[member.display_name] = I.empty()

@bot.event
async def on_member_remove(member):
    if not member.bot:
        del time_intervals[member.display_name]

@bot.event
async def on_member_update(before, after):
    if not after.bot:
        time_intervals[after.display_name] = time_intervals.pop(before.display_name)

@bot.event
async def on_user_update(before, after):
    if not after.bot:
        time_intervals[after.display_name] = time_intervals.pop(before.display_name)

@bot.event
async def on_command_error(ctx, error):
    title = 'ERROR'

    if isinstance(error, commands.CheckFailure):
        await ctx.send('You are not allowed to do this.')

        title = 'CheckFailure'

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('A required argument is missing.')

        title = 'MissingRequiredArgument'

    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('This command does not exist. Did you misspell it?')

        title = 'CommandNotFound'

    elif isinstance(error, commands.TooManyArguments):
        await ctx.send('You entered too many Arguments.')

        title = 'MissingRequiredArgument'

    await send_state_in_discord(title)

    # enable for debugging
    # raise error

@bot.event
async def on_disconnect():
    keep_saving.stop()

    save_time_intervals()

bot.run(TOKEN)