from collections.abc import Awaitable, Callable

from asyncio import Future

from typing import Any

import asyncio


import logging


class SignalException(Exception):
    pass


class ConnectionNotFoundException(SignalException):
    pass


class Connection[**P]:
    def __init__(
        self, signal: "Signal[P]", callback: Callable[P, Awaitable[Any]]
    ) -> None:
        self.logger = logging.getLogger(__name__ + ".Connection")
        self.callback: Callable[P, Awaitable[Any]] = callback
        self.signal = signal

    async def fire(self, *args: P.args, **kwargs: P.kwargs) -> None:
        if self.callback is not None:
            self.logger.debug(
                f"Firing callback {self.callback} with args={args}, kwargs={kwargs}"
            )
            await self.callback(*args, **kwargs)

    @property
    def is_connected(self) -> bool:
        return self in self.signal.connections

    def disconnect(self) -> None:
        self.logger.debug("Disconnecting connection.")
        self.signal.disconnect(self)


class Signal[**P]:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__ + ".Signal")
        self.connections: list[Connection[P]] = []

    def connect(self, callback: Callable[P, Awaitable[Any]]) -> Connection[P]:
        self.logger.debug(f"Connecting callback: {callback}")
        connection = Connection[P](self, callback)
        self.connections.append(connection)
        return connection

    def disconnect(self, connection: Connection[P]) -> None:
        if not connection in self.connections:
            self.logger.error("Connection not found during disconnect.")
            raise ConnectionNotFoundException()
        self.logger.debug("Disconnecting connection.")
        self.connections.remove(connection)

    def emit(self, *args: P.args, **kwargs: P.kwargs) -> Future[list[None]]:
        if not self.connections:
            future: Future[list[None]] = asyncio.get_event_loop().create_future()
            future.set_result([])
            return future
        self.logger.debug(
            f"Emitting signal to {len(self.connections)} connections with args={args}, kwargs={kwargs}"
        )
        return asyncio.gather(
            *(connection.fire(*args, **kwargs) for connection in self.connections)
        )

    async def wait(self) -> None:
        self.logger.debug("Waiting for signal emission.")
        future: Future[None] = asyncio.get_event_loop().create_future()

        async def _on_emit(*args: P.args, **kwargs: P.kwargs) -> None:
            future.set_result(None)

        connection = self.connect(_on_emit)
        try:
            await future
        finally:
            connection.disconnect()

    def once(self, callback: Callable[P, Awaitable[Any]]) -> Connection[P]:
        connection: Connection[P]

        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            if connection:
                self.logger.debug("Disconnecting after one emission.")
                connection.disconnect()
            await callback(*args, **kwargs)

        connection = self.connect(wrapper)
        return connection
