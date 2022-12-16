# confess-bot
#
# Copyright (c) 2022 Andrey V
# All rights reserved.
#
# This code is licensed under the 3-clause BSD License.
# See the LICENSE file at the root of this project.

"""DB connection and setup helpers."""

from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine

from dbmodel import prepare_database

__funcs = ('start_db', 'stop_db')

__all__ = (*__funcs, 'db_engine')

DB_URL = config('DB_URL')

db_engine = create_async_engine(DB_URL)


async def start_db():
    """Start the database. Intended to be run at service start-up."""
    async with db_engine.begin() as a_sess:
        await prepare_database(a_sess)


async def stop_db():
    """Stop the database. Intended to be run at service shut-down, if applicable."""
    await db_engine.dispose()
