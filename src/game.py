import pygame

from src.utilities.context import Context

pygame.init()

from src.components.dispatcher import Dispatcher
from src.components.window import Window
from src.components.clock import Clock
from src.components.stage import Stage

class Game:
    def __init__(self):
        self.dispatcher = Dispatcher() 
        self.window = Window()
        self.clock = Clock()
        self.stage = Stage(Context(window=self.window))
        self.running = False

    async def initialize(self) -> None:
        async def on_quit(event: pygame.event.Event) -> None:
            print("Received quit event, stopping game loop at next tick...")
            self.stop()
        self.dispatcher.get_signal_for(pygame.QUIT).connect(on_quit)

    async def tick(self) -> None:
        await self.dispatcher.process_events()
        await self.clock.tick()

    async def run(self) -> None:
        self.running = True
        while self.running:
            await self.tick()
        pygame.quit()

    def stop(self) -> None:
        self.running = False
