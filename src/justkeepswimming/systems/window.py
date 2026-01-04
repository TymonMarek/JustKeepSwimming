import logging

import pygame
from pygame import Vector2

from justkeepswimming.systems.dispatcher import Dispatcher

DEFAULT_WINDOW_TITLE: str = "Just Keep Swimming!"
DEFAULT_WINDOW_SIZE: Vector2 = Vector2(800, 600)
DEFAULT_WINDOW_FLAGS: int = pygame.RESIZABLE
DEFAULT_IS_VSYNC_ENABLED: bool = False


class Window:
    def __init__(self, dispatcher: Dispatcher) -> None:
        self.logger = logging.getLogger("Window")
        self._title: str = DEFAULT_WINDOW_TITLE
        self._size: Vector2 = DEFAULT_WINDOW_SIZE
        self._vsync_enabled: bool = DEFAULT_IS_VSYNC_ENABLED
        self._flags: int = DEFAULT_WINDOW_FLAGS
        self.on_resize = dispatcher.get_signal_for(pygame.VIDEORESIZE)
        self.surface: pygame.Surface
        self._create_window()
        self.on_resize.connect(self._on_resize_event)

    async def _on_resize_event(self, event: pygame.event.Event) -> None:
        self._size = Vector2(event.w, event.h)

    def refresh(self):
        pygame.display.flip()

    def _create_window(self):
        self.logger.debug(
            f"Creating window: title={self._title}, size={self._size}, vsync={self._vsync_enabled}, flags={self._flags}"
        )
        self.surface = pygame.display.set_mode(
            self._size, flags=self._flags, vsync=self._vsync_enabled
        )
        pygame.display.set_caption(self._title)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self.logger.debug(f"Setting window title: {value}")
        self._title = value
        pygame.display.set_caption(self._title)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: Vector2):
        self.logger.debug(f"Setting window size: {value}")
        self._size = value
        self._create_window()

    @property
    def vsync(self):
        return self._vsync_enabled

    @vsync.setter
    def vsync(self, value: bool):
        self.logger.debug(f"Setting vsync: {value}")
        self._vsync_enabled = value
        self._create_window()

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, value: int):
        self.logger.debug(f"Setting window flags: {value}")
        self._flags = value
        self._create_window()
