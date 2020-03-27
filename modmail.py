import discord
from discord.ext import commands
import logging
import db_connection as db


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
        # ticket_id_request = (message.author.id, )
        ticket_row = db.select_ticket('discord_user', message.author.id)


        # if not open ticket, make new ticket
        if not ticket_row:
            # ticket_request = (message.author.id, 'open', 0)
            ticket_id = db.create_ticket(message.author.id)
        else:
            ticket_id = ticket_row['id']

        msg_id = db.create_msg_log(ticket_id, message.author, message.content)

        # log info to ticket in db
        await message.channel.send(f'ill send help! pls wait for a reply.')  # DM answer, only for testing

        await update_ticket(ticket_id)
        # channel_mod_mail = await bot.fetch_channel(channel_id_mod_mail)
        # # pass msg to modmail channel
        # # TODO: format msg using discord package formatting
        # # mod_mail_msg = f"uid: {message.author.id} - author: {message.author}: \n{message.content}"
        # ticket_row = db.select_ticket('id', ticket_id)
        # if not ticket_row['bot_msg_id'] == 0:
        #     old_bot_msg = await channel_mod_mail.fetch_message(ticket_row['bot_msg_id'])
        #     await old_bot_msg.delete()
        # msg_rows = db.select_msg_logs('ticket_id', ticket_id)
        # mod_mail_msg = f"``` ticket id: {ticket_row['id']}, user: {message.author} \n"
        # for row in msg_rows:
        #     mod_mail_msg += f"{row['sender']}: {row['msg_content']} \n"
        # mod_mail_msg += "```"
        # bot_msg = await channel_mod_mail.send(mod_mail_msg)
        # db.update_ticket('bot_msg_id', 'id', ticket_id, bot_msg.id)

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
async def answer(ctx, ticket_id_input: int, *, msg_text):
    # TODO: lookup ticket id in db
    # ticket_id_request = (ticket_id_input,)
    # ticket_id = db.get_user_ticket_wrapper(ticket_id_request)
    ticket_row = db.select_ticket('id', ticket_id_input)

    if not ticket_row:
        error_msg = await ctx.send(f"Error: Ticket number {ticket_id_input} not found.")
        error_msg.id.delete(delay=5)
        return
    # log answer in db
    db.create_msg_log(ticket_id_input, ctx.author, msg_text)

    # send answer to user DM
    user = await bot.fetch_user(ticket_row['discord_user'])
    user_dm_channel = user.dm_channel
    if not user_dm_channel:
        await user.create_dm()
        user_dm_channel = user.dm_channel
    await user_dm_channel.send(f'{msg_text}')
    await update_ticket(ticket_id_input)
    await ctx.message.delete(delay=3)


@bot.command()
@is_mod_mail_channel()
async def close(ctx, ticket_id: int):
    ticket_row = db.select_ticket('id', ticket_id)
    db.update_ticket('status', 'id', ticket_id, "'closed'")
    channel_mod_mail = await bot.fetch_channel(channel_id_mod_mail)
    old_bot_msg = await channel_mod_mail.fetch_message(ticket_row['bot_msg_id'])
    await old_bot_msg.delete()


async def update_ticket(ticket_id):

    channel_mod_mail = await bot.fetch_channel(channel_id_mod_mail)
    # TODO: format msg using discord package formatting
    ticket_row = db.select_ticket('id', ticket_id)
    if not ticket_row['bot_msg_id'] == 0:  # 0 is placeholder in new tickets
        old_bot_msg = await channel_mod_mail.fetch_message(ticket_row['bot_msg_id'])
        await old_bot_msg.delete()

    # build display msg string
    msg_rows = db.select_msg_logs('ticket_id', ticket_id)
    mod_mail_msg = f"``` ticket id: {ticket_row['id']}, user: {msg_rows[0]['sender']} \n"
    for row in msg_rows:
        mod_mail_msg += f"{row['sender']}: {row['msg_content']} \n"
    mod_mail_msg += "```"
    bot_msg = await channel_mod_mail.send(mod_mail_msg)
    db.update_ticket('bot_msg_id', 'id', ticket_id, bot_msg.id)



bot.run(TOKEN)
