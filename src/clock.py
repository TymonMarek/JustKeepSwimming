from dataclasses import dataclass
import pygame

@dataclass
class Tick:
    delta_time: float


class Clock:
    def __init__(self) -> None:
        self.__clock = pygame.time.Clock()
        self.delta_time = 0.00
        self.tickrate: int = 0

    async def tick(self) -> Tick:
        self.delta_time = self.__clock.tick(self.tickrate)  / 1000
        return Tick(self.delta_time)