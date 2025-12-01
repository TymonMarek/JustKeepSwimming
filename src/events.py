from collections import defaultdict
from typing import Any, Callable, DefaultDict

import pygame

from clock import Tick
from emitter import Emitter, Observer

class Events:
    """A wrapper class for handling, dispatching and binding to specific pygame events.
    """
    def __init__(self) -> None:
        self.bindings: DefaultDict[int, Emitter[Tick, pygame.event.Event]] = defaultdict(Emitter)

    def bind(self, event_type: int, callback: Callable[[Tick, pygame.event.Event], Any]) -> Observer[Tick, pygame.event.Event]:
        """Binds the current callback to the specified event type using an `Emitter`.
        The callback will be invoked every time the event is emitted, even if it occurs multiple times in a single tick.

        Args:
            event_type (int): The pygame event ID to bind to. (Can be found in `pygame.locals`)
            callback (Callable[[Tick, pygame.event.Event], Any]): The callback to be invoked when the event is emitted.
        """
        observer = self.bindings[event_type].observe(callback)
        return observer

    async def tick(self, tick: Tick) -> None:
        """Processes all pygame events for the current tick and emits them to their respective bindings.

        Args:
            tick (Tick): The current tick instance.
        """
        for event in pygame.event.get():
            await self.bindings[event.type].emit(tick, event)
    