from dataclasses import dataclass
from typing import Optional

from pygame.time import Clock as PygameClock

from src.utilities.signal import Signal

from datetime import datetime

PYGAME_DELTA_TIME_SCALE = 0.001


class ClockException(Exception):
    pass


class ClockNotRunningException(ClockException):
    pass


@dataclass
class TickData:
    delta_time: float


import logging


class Clock:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".Clock")
        self.on_tick = Signal()
        self.target_framerate: Optional[int] = None
        self.start_timestamp: Optional[float] = None
        self.__pygame_clock = PygameClock()
        self.running = False

    async def tick(self):
        delta_time: float = (
            self.__pygame_clock.tick(self.target_framerate or 0)
            * PYGAME_DELTA_TIME_SCALE
        )
        tick_data = TickData(delta_time)
        await self.on_tick.emit(tick_data)

    async def run(self):
        self.logger.info("Clock started.")
        self.running = True
        self.start_timestamp = datetime.now().timestamp()
        while self.running:
            await self.tick()

    def stop(self):
        if not self.running:
            raise ClockNotRunningException()
        self.running = False
        self.start_timestamp = None
