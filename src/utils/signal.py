from collections.abc import Awaitable, Callable

from asyncio import Future

from typing import Any

import asyncio


class SignalException(Exception):
    pass


class ConnectionNotFoundException(SignalException):
    pass


class Connection[**P]:
    def __init__(
        self, signal: "Signal[P]", callback: Callable[P, Awaitable[Any]]
    ) -> None:
        self.callback: Callable[P, Awaitable[Any]] = callback
        self.signal = signal

    async def fire(self, *args: P.args, **kwargs: P.kwargs) -> None:
        if self.callback is not None:
            await self.callback(*args, **kwargs)
            
    @property
    def is_connected(self) -> bool:
        return self in self.signal.connections

    def disconnect(self) -> None:
        self.signal.disconnect(self)


class Signal[**P]:
    def __init__(self) -> None:
        self.connections: list[Connection[P]] = []

    def connect(self, callback: Callable[P, Awaitable[Any]]) -> Connection[P]:
        connection = Connection[P](self, callback)
        self.connections.append(connection)
        return connection

    def disconnect(self, connection: Connection[P]) -> None:
        if not connection in self.connections:
            raise ConnectionNotFoundException()
        self.connections.remove(connection)

    def emit(self, *args: P.args, **kwargs: P.kwargs) -> Future[list[None]]:
        return asyncio.gather(
            *(connection.fire(*args, **kwargs) for connection in self.connections)
        )

    async def wait(self) -> None:
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
                connection.disconnect()
            await callback(*args, **kwargs)

        connection = self.connect(wrapper)

        return connection
