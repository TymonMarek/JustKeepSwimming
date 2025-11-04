from collections import defaultdict
from typing import Any, Callable, DefaultDict

import pygame

from clock import Tick
from emitter import Emitter

class Events:
    def __init__(self) -> None:
        self.bindings: DefaultDict[int, Emitter[Tick, pygame.event.Event]] = defaultdict(Emitter)

    def bind(self, event_type: int, callback: Callable[[Tick, pygame.event.Event], Any]):
        self.bindings[event_type].listen(callback)

    async def tick(self, tick: Tick) -> None:
        for event in pygame.event.get():
            await self.bindings[event.type].emit(tick, event)
