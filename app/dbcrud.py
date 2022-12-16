# confess-bot
#
# Copyright (c) 2022 Andrey V
# All rights reserved.
#
# This code is licensed under the 3-clause BSD License.
# See the LICENSE file at the root of this project.

"""
The DB CRUD helper responsible for dealing with users.
"""

from typing import List, Optional, Union

from sqlalchemy import select

from dbmodel import server

__all__ = ('ServerCrud',)


class ServerCrud:
    """"
    Server mapping management helper.

    Database session is used to query and manage users and the
    io wrapper is used to commit deletes for workouts of deleted users.
    """
    __slots__ = ('db_session',)

    def __init__(self, db):
        self.db_session = db

    async def get(self, server_id: int) -> Optional[int]:
        """Get a channel number for a server. Return None if no match."""
        query = select(server.c.dest_channel_id).where(server.c.server_id == server_id)

        async with self.db_session.connect() as conn:
            row = (await conn.execute(query)).one_or_none()
            if row is not None:
                return row[0]


    async def create(self, server_id: int, channel_id: Optional[int] = None) -> bool:
        """Create a new server map entry with optional initial channel."""
        query = server.insert().values(server_id=server_id)

        async with self.db_session.begin() as txn:
            return (await txn.execute(query)).rowcount == 1

    async def update(self, server_id: int, channel_id: int) -> bool:
        """Update the mapping matching the server value model User where the userid matches.

        Return whether a matching server_id was found.
        """
        query = server.update().where(server.c.server_id == server_id). \
            values(dest_channel_id=channel_id)

        async with self.db_session.begin() as txn:
            return (await txn.execute(query)).rowcount == 1

    async def delete(self, server_id: int) -> bool:
        """Delete a mapping.

        Return whether success or failure."""
        query = server.delete().where(server.id == server_id)

        async with self.db_session.begin() as txn:
            return (await txn.execute(query)).rowcount == 1
