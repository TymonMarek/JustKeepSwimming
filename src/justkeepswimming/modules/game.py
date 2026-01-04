import asyncio

import os
import time

from justkeepswimming.scenes import SceneID, default

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
from logging import getLogger

from justkeepswimming.utilities.context import GameContext

pygame.init()

from justkeepswimming.modules.dispatcher import Dispatcher
from justkeepswimming.modules.window import Window
from justkeepswimming.modules.clock import Clock, TickContext
from justkeepswimming.modules.stage import Stage


class Game:
    def __init__(self):
        self.time_started = time.time()
        self.logger = getLogger(__name__)
        self.logger.info("Initializing...")
        self.dispatcher = Dispatcher()
        self.window = Window(self.dispatcher)
        self.clock = Clock()

        self.context = GameContext(
            clock=self.clock,
            window=self.window,
            dispatcher=self.dispatcher,
        )

        self.stage = Stage(
            self.context,
            {
                SceneID.DEFAULT: default.load,
            },
        )

        self._attach_quit_handler()
        self.clock.on_tick.connect(self._process_game)

    def _attach_quit_handler(self) -> None:
        self.logger.debug("Setting up quit event handler.")

        async def _on_quit(event: pygame.event.Event) -> None:
            self.logger.info("Exiting on the next tick...")
            await self._quit()

        self.dispatcher.get_signal_for(pygame.QUIT).connect(_on_quit)

    async def _process_game(self, tick_context: TickContext) -> None:
        await self.dispatcher.process_events()
        await self.stage.on_tick.emit(tick_context, self.context)

    async def start(self) -> None:
        asyncio.create_task(self.clock.on_start.emit())
        self.logger.info(f"Ready in {time.time() - self.time_started:.2f} seconds!")

    async def _quit(self) -> None:
        self.logger.info("Stopping process...")
        await self.clock.on_stop.emit()
