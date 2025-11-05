import sys
import pygame

from clock import Clock
from events import Events
from input import Input
from render import Window

pygame.init()

class Game:
    def __init__(self) -> None:
        self.clock = Clock()
        self.events = Events()
        self.input = Input()
        self.window = Window()
        self.running: bool = False
        self.__post_init__()

    def __post_init__(self) -> None:
        self.events.bind(pygame.MOUSEBUTTONDOWN, self.input.mouse.buttons.on_pressed)
        self.events.bind(pygame.MOUSEBUTTONUP, self.input.mouse.buttons.on_released)
        self.events.bind(pygame.MOUSEWHEEL, self.input.mouse.scroll.on_scroll)
        self.events.bind(pygame.MOUSEMOTION, self.input.mouse.on_mouse_moved)
        self.events.bind(pygame.KEYDOWN, self.input.keyboard.on_key_pressed)
        self.events.bind(pygame.KEYUP, self.input.keyboard.on_key_released)
        self.events.bind(pygame.QUIT, lambda tick, event: self.quit())

    def quit(self) -> None:
        self.running = False

    async def run(self) -> None:
        self.running = True
        try:
            while self.running:
                tick = await self.clock.tick()
                await self.events.tick(tick)
                self.window.render()
                self.window.flip()
        except KeyboardInterrupt:
            pass
        pygame.quit()
        sys.exit(0)