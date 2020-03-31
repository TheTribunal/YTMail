import discord
from discord.ext import commands
import logging
import db_connection as db


logging.basicConfig(level=logging.INFO)

# TODO: store channel ids externally
channel_id_mod_mail = 692763885941555270

with open('token_modmail_yt_testserver.txt', 'r') as f:
    TOKEN = f.read().rstrip()

# ignored_users = db.get_ignored_users_list()

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():  # on starting bot
    print(f'We have logged in as {bot.user}')
    # TODO read ignored users list from db into memory
    # ignored_user = db.get_ignored_users_list()
    # ignored_users = []  # dummy list


@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages from self
        return
    # if message.author.id in ignored_users:  # ignores ANY msg from ignored users, no interaction possible
    #     return

    if isinstance(message.channel, discord.DMChannel) and message.author.id not in db.get_ignored_users_list():  # only listen to dm
        ticket_row = db.select_ticket('discord_user', message.author.id)

        # if not open ticket, make new ticket
        if not ticket_row:
            ticket_id = db.create_ticket(message.author.id)
            await message.channel.send(f'ill send help! pls wait for a reply.')  # DM answer, only for testing
        else:
            ticket_id = ticket_row['id']

        # log ticket to db
        msg_id = db.create_msg_log(ticket_id, message.author, message.content)

        await update_ticket_display(ticket_id)

    await bot.process_commands(message)  # needed so the bot listens to commands

    # TODO: find a proper place to keep mod mail channel clean
    # remove msgs from mod mail channel
    if message.channel.id == channel_id_mod_mail:
        await message.delete(delay=3)


# this is the decorator for mod mail channel only commands
def is_mod_mail_channel():
    async def predicate(ctx):
        return ctx.channel.id == channel_id_mod_mail
    return commands.check(predicate)


@bot.command()
@is_mod_mail_channel()
async def answer(ctx, ticket_id_input: int, *, msg_text):
    ticket_row = db.select_ticket('id', ticket_id_input)

    if not ticket_row:
        error_msg = await ctx.send(f"Error: Ticket number {ticket_id_input} not found.")
        await error_msg.id.delete(delay=5)
        return

    db.create_msg_log(ticket_id_input, ctx.author, msg_text)

    # send answer to user DM
    user = await bot.fetch_user(ticket_row['discord_user'])
    user_dm_channel = user.dm_channel
    if not user_dm_channel:
        await user.create_dm()
        user_dm_channel = user.dm_channel
    await user_dm_channel.send(f'{msg_text}')
    await update_ticket_display(ticket_id_input)
    await ctx.message.delete(delay=3)


@bot.command()
@is_mod_mail_channel()
async def close(ctx, ticket_id: int):
    ticket_row = db.select_ticket('id', ticket_id)
    db.update_ticket('status', 'id', ticket_id, "'closed'")
    channel_mod_mail = await bot.fetch_channel(channel_id_mod_mail)
    old_bot_msg = await channel_mod_mail.fetch_message(ticket_row['bot_msg_id'])
    user_obj = await bot.fetch_user(ticket_row['discord_user'])
    await user_obj.send(f'Your ticket has been closed.')
    await old_bot_msg.delete()
    return ticket_row


@bot.command()
@is_mod_mail_channel()
async def ignore(ctx, ticket_id: int):
    ticket_row = await close(ctx, ticket_id)
    # add to ignore ticket_row['discord_user']
    db.add_ignored_user(ticket_row['discord_user'])
    # update ignored users in memory
    # bot.ignored_users = db.get_ignored_users_list()
    user = await bot.fetch_user(ticket_row['discord_user'])
    bot_msg = await ctx.send(f'Set discord_uid {ticket_row["discord_user"]} - {user} to ignored.')

    await bot_msg.delete(delay=10)


@bot.command()
@is_mod_mail_channel()
async def stop_ignore(ctx, discord_user_id):
    db.remove_ignored_user(discord_user_id)
    # bot.ignored_users = db.get_ignored_users_list()
    bot_msg = await ctx.send(f'Okay, ill hear what uid {discord_user_id} has to say.')
    await bot_msg.delete(delay=10)


@bot.command()
@is_mod_mail_channel()
async def list_ignored(ctx):
    ignored_users = db.get_ignored_users_list()
    ignored_user_objects = []
    print(ignored_users)
    for u in ignored_users:
        print(u)
        u_obj = await bot.fetch_user(u)
        print(u_obj)
        ignored_user_objects.append(u_obj)
    print(ignored_user_objects)
    ignored_u_list = [f'{u.__str__()} - {u.id}' for u in ignored_user_objects]
    ignored_msg = await ctx.send(ignored_u_list)
    await ignored_msg.delete(delay=10)


async def update_ticket_display(ticket_id):
    """
    creates a new text block with current msg logs for a ticket in mod mail channel
    deletes the old msg block
    :param ticket_id:
    """
    channel_mod_mail = await bot.fetch_channel(channel_id_mod_mail)
    ticket_row = db.select_ticket('id', ticket_id)
    if not ticket_row['bot_msg_id'] == 0:  # 0 is placeholder in new tickets
        old_bot_msg = await channel_mod_mail.fetch_message(ticket_row['bot_msg_id'])
        await old_bot_msg.delete()

    # build display msg string
    msg_rows = db.select_multiple_msg_logs('ticket_id', ticket_id)
    # TODO: format msg using discord package formatting
    mod_mail_msg = f"``` ticket id: {ticket_row['id']}, user: {msg_rows[0]['sender']} \n"
    for row in msg_rows:
        mod_mail_msg += f"{row['sender']}: {row['msg_content']} \n"
    mod_mail_msg += "```"
    bot_msg = await channel_mod_mail.send(mod_mail_msg)

    db.update_ticket('bot_msg_id', 'id', ticket_id, bot_msg.id)





bot.run(TOKEN)
