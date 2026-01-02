from typing import Any

from src.utilities.signal import Connection


class Maid:
    def __init__(self) -> None:
        self._connections: list[Connection[Any]] = []

    def add(self, connection: Connection[Any]) -> None:
        self._connections.append(connection)

    def cleanup(self) -> None:
        for connection in self._connections:
            try:
                connection.disconnect()
            except (
                Exception
            ):  # We really don't care if disconnecting fails, since we're cleaning up anyway.
                if connection in connection.signal.connections:
                    connection.signal.disconnect(
                        connection
                    )  # Just make sure it's disconnected if there was an exception.
        self._connections.clear()
