
import pygame
import logging

from src.utilities.context import Context

pygame.init()

from src.components.dispatcher import Dispatcher
from src.components.window import Window
from src.components.clock import Clock
from src.components.stage import Stage

logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        logger.info("Initializing process...")
        self.dispatcher = Dispatcher()
        self.window = Window()
        self.clock = Clock()
        self.stage = Stage(Context(window=self.window))
        self.running = False

    async def initialize(self) -> None:
        logger.debug("Setting up quit event handler.")
        async def on_quit(event: pygame.event.Event) -> None:
            logger.info("Received QUIT, exiting the game on the next tick...")
            self.stop()
        self.dispatcher.get_signal_for(pygame.QUIT).connect(on_quit)

    async def tick(self) -> None:
        await self.dispatcher.process_events()
        await self.clock.tick()

    async def run(self) -> None:
        logger.info("Process ready!")
        self.running = True
        while self.running:
            await self.tick()
        logger.info("Exiting process...")
        pygame.quit()
        import sys
        sys.exit(0)

    def stop(self) -> None:
        logger.info("Stopping game loop...")
        self.running = False
