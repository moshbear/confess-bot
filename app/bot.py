# confess-bot
#
# Copyright (c) 2022 Andrey V
# All rights reserved.
#
# This code is licensed under the 3-clause BSD License.
# See the LICENSE file at the root of this project.
import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands

from decouple import config

from dbconn import start_db, db_engine
from dbcrud import ServerCrud

_setup_msg = """
confessbot setup:

/csetchan <target-channel>

you must have channel management permissions to use this command
"""

_L = logging.getLogger('bot')

asyncio.run(start_db())
db_crud = ServerCrud(db=db_engine)

bot = commands.Bot(intents=discord.Intents(guilds=True), loop=asyncio.new_event_loop())


# DB interface


async def _create_server(server_id: int, channel_id: Optional[int] = None) -> bool:
    return await db_crud.create(server_id, channel_id)


async def _get_channel_for_server(server_id: int) -> Optional[int]:
    return await db_crud.get(server_id)


async def _set_channel_for_server(server_id: int, channel_id: int) -> bool:
    return await db_crud.update(server_id, channel_id)


async def _delete_server(server_id: int) -> bool:
    return await db_crud.delete(server_id)


# Discord interface


async def _send_ephemeral_msg(ctx: discord.ApplicationContext, message: str):
    await ctx.send_response(message, ephemeral=True)


@bot.slash_command(name='confess')
async def confess(ctx: discord.ApplicationContext, message: discord.Option(str)):
    target_id = await _get_channel_for_server(ctx.guild_id)
    target = ctx.guild.get_channel(target_id)
    if target is None:
        await _send_ephemeral_msg(ctx, f'Could not find channel for id {target_id}')
        return
    try:
        await target.send(message)
        await _send_ephemeral_msg(ctx, 'Sent')
    except discord.Forbidden:
        await _send_ephemeral_msg(ctx, f'Permission error sending to "{target.name}"')


@bot.slash_command(name='csetchan')
@commands.has_permissions(manage_channels=True)
async def set_channel(ctx: discord.ApplicationContext, channel: discord.Option(str)):
    if not (channel.startswith('<#') and channel.endswith('>')):
        _L.warning(f'Can\'t parse channel str "{channel}"')
        await _send_ephemeral_msg(ctx, 'Couldn\'t set channel; see log')
        return
    try:
        channel_id = int(channel[2:-1])
    except ValueError as e:
        await ctx.send_response(f'bad int: {e}')
        return
    # this would've been cleaner as an UPSERT
    if (await _set_channel_for_server(ctx.guild_id, channel_id)) \
            or (await _create_server(ctx.guild_id, channel_id)):
        await _send_ephemeral_msg(ctx, f'Set channel to #{ctx.guild.get_channel(channel_id).name}')
    else:
        await _send_ephemeral_msg(ctx, 'DB failed to set channel')


@bot.event
async def on_guild_join(guild: discord.Guild):
    await _create_server(guild.id)
    if (chan := guild.system_channel) is not None:
        await chan.send(_setup_msg)
        return
    for chan in await guild.fetch_channels():
        if not isinstance(chan, discord.TextChannel):
            continue
        try:
            await chan.send(_setup_msg)
            return
        except discord.Forbidden:
            continue
    _L.warning('guild "%s" <%d>: no available channel to send setup message to', guild.name, guild.id)


@bot.event
async def on_guild_remove(guild):
    await _delete_server(guild.id)


bot.run(config('DISCORD_TOKEN'))

