from pygame import Vector2

import pygame


DEFAULT_WINDOW_TITLE: str = "Default Window"
DEFAULT_WINDOW_SIZE: Vector2 = Vector2(800, 600)
DEFAULT_WINDOW_FLAGS: int = pygame.SCALED | pygame.RESIZABLE
DEFAULT_IS_VSYNC_ENABLED: bool = False


class Window:
    def __init__(self):
        self._title: str = DEFAULT_WINDOW_TITLE
        self._size: Vector2 = DEFAULT_WINDOW_SIZE
        self._vsync_enabled: bool = DEFAULT_IS_VSYNC_ENABLED
        self._flags: int = DEFAULT_WINDOW_FLAGS
        self.surface: pygame.Surface
        self._create_window()
        
    def _create_window(self):
        self.surface = pygame.display.set_mode(self._size, flags=self._flags, vsync=self._vsync_enabled)
        pygame.display.set_caption(self._title)
                
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value: str):
        self._title = value
        pygame.display.set_caption(self._title)
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value: Vector2):
        self._size = value
        self._create_window()

    @property
    def vsync(self):
        return self._vsync_enabled
    
    @vsync.setter
    def vsync(self, value: bool):
        self._vsync_enabled = value
        self._create_window()
        
    @property
    def flags(self):
        return self._flags
    
    @flags.setter
    def flags(self, value: int):
        self._flags = value
        self._create_window()

