import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pygame.time import Clock as PygameClock

from justkeepswimming.utilities.signal import Signal

PYGAME_DELTA_TIME_SCALE = 0.001


class ClockException(Exception):
    pass


class ClockNotRunningException(ClockException):
    pass


class ClockAlreadyRunningException(ClockException):
    pass


@dataclass(frozen=True)
class TickContext:
    delta_time: float


class Clock:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".Clock")
        self.on_tick = Signal()
        self.target_framerate: Optional[int] = None
        self.start_timestamp: Optional[float] = None
        self.__pygame_clock = PygameClock()
        self.on_start = Signal()
        self.on_stop = Signal()
        self.running = False
        self.on_start.connect(self._start)
        self.on_stop.connect(self._stop)

    async def _start(self):
        if self.running:
            raise ClockAlreadyRunningException()
        self.running = True
        self.start_timestamp = datetime.now().timestamp()
        while self.running:
            await self._tick()

    async def _tick(self):
        delta_time: float = (
            self.__pygame_clock.tick(self.target_framerate or 0)
            * PYGAME_DELTA_TIME_SCALE
        )
        tick_data = TickContext(delta_time)
        await self.on_tick.emit(tick_data)

    async def _stop(self):
        if not self.running:
            raise ClockNotRunningException()
        self.running = False
        self.start_timestamp = None
