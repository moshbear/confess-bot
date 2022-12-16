# confess-bot
#
# Copyright (c) 2022 Andrey V
# All rights reserved.
#
# This code is licensed under the 3-clause BSD License.
# See the LICENSE file at the root of this project.

"""Database models."""

from sqlalchemy import MetaData, Table, Column, BigInteger
from sqlalchemy.engine import Connection

__all__ = (
    'server',
    'prepare_database'
)

meta = MetaData()

server = Table("server", meta,
               Column("server_id", BigInteger, primary_key=True),
               Column("dest_channel_id", BigInteger, nullable=True, default=None)
               )


# pylint: disable=unused-argument
def _do_prepare_database(conn: Connection, *args, **kwargs):
    """Performs auxiliary database setup steps after initializing tables and indices."""
    pass


# FIXME: type(AsyncEngine().begin()) is a mess to get working but is necessary to annotate a_sess
async def prepare_database(a_sess):
    """Prepares the database using the async session a_sess."""
    await a_sess.run_sync(meta.create_all, checkfirst=True)
    await a_sess.run_sync(_do_prepare_database)
