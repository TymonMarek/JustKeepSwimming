from pygame import Vector2

import pygame


DEFAULT_WINDOW_TITLE: str = "Default Window"
DEFAULT_WINDOW_SIZE: Vector2 = Vector2(800, 600)
DEFAULT_WINDOW_FLAGS: int = pygame.SCALED | pygame.RESIZABLE
DEFAULT_IS_VSYNC_ENABLED: bool = False


import logging

class Window:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".Window")
        self._title: str = DEFAULT_WINDOW_TITLE
        self._size: Vector2 = DEFAULT_WINDOW_SIZE
        self._vsync_enabled: bool = DEFAULT_IS_VSYNC_ENABLED
        self._flags: int = DEFAULT_WINDOW_FLAGS
        self.surface: pygame.Surface
        self._create_window()

    def _create_window(self):
        self.logger.debug(f"Creating window: title={self._title}, size={self._size}, vsync={self._vsync_enabled}, flags={self._flags}")
        self.surface = pygame.display.set_mode(self._size, flags=self._flags, vsync=self._vsync_enabled)
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

