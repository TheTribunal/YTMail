import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)

# TODO: store channel ids externally
channel_id_mod_mail = 692763885941555270

with open('token_modmail_yt_testserver.txt', 'r') as f:
    TOKEN = f.read().rstrip()

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():  # on starting bot
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages from self
        return
    if isinstance(message.channel, discord.DMChannel):  # only listen to dm
        # TODO: check db for open ticket
        # if not open ticket, make new ticket
        # log info to ticket in db
        await message.channel.send(f'ill send help! pls wait for a reply.')  # DM answer, only for testing
        channel_mod_mail = await bot.fetch_channel(channel_id_mod_mail)

        # pass msg to modmail channel
        # TODO: format msg using discord package formatting
        mod_mail_msg = f"uid: {message.author.id} - author: {message.author}: \n{message.content}"
        await channel_mod_mail.send(mod_mail_msg)

    await bot.process_commands(message)  # needed so the bot listens to commands

    # TODO: find a proper place to keep modmail channel clean
    # remove msgs from modmail channel
    if message.channel.id == channel_id_mod_mail:
        await message.delete(delay=3)


# this is the decorator for mod mail channel only stuff
def is_mod_mail_channel():
    async def predicate(ctx):
        return ctx.channel.id == channel_id_mod_mail
    return commands.check(predicate)


@bot.command()
@is_mod_mail_channel()
async def answer(ctx, ticket_id, *, arg):
    # TODO: lookup ticket id in db
    # get user_id from ticket
    # log answer in db
    # send answer to user DM
    user = await bot.fetch_user(ticket_id)
    user_dm_channel = user.dm_channel
    if not user_dm_channel:
        await user.create_dm()
        user_dm_channel = user.dm_channel
        await user_dm_channel.send(f'{arg}')

        # remove mod msg from channel
        # await ctx.message.delete(delay=3)


@bot.command()
@is_mod_mail_channel()
async def close(ctx, ticket_id):
    # remove ticket msg block from channel
    # ticket_msg = get msg.id from db
    # ticket_msg.delete()
    # update ticket status in db to "closed"
    pass

bot.run(TOKEN)
