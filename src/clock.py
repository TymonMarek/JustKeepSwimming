from dataclasses import dataclass
import pygame

@dataclass
class Tick:
    """A tick object is a dataclass that encapsulates data about the current tick.
    """
    delta_time: float


class Clock:
    """A wrapper for the Pygame clock object that handles tick timings and delta time calculations.
    """
    def __init__(self) -> None:
        self.__clock = pygame.time.Clock()
        self.delta_time = 0.00
        self.tickrate: int = 0

    async def tick(self) -> Tick:
        """Tick the internal clock at the tickrate specified with `Clock.tickrate`. If it is 0, will run without a fixed tickrate target.

        Returns:
            Tick: The tick object containing the delta time since the last tick.
        """
        self.delta_time = self.__clock.tick(self.tickrate)  / 1000
        return Tick(self.delta_time)