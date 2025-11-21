import pygame

from clock import Tick
from emitter import Emitter
import sprites

class Window:
    """A class representing the main application window.
    """
    def __init__(self) -> None:
        self.surface = pygame.display.set_mode()
        self._title = pygame.display.get_caption()[0]
        self.resized = Emitter[pygame.Vector2]()
        self._size = pygame.Vector2()

    @property
    def size(self) -> pygame.Vector2:
        return self._size
    
    @size.setter
    async def size(self, size: pygame.Vector2):
        if size == self._size:
            return
        await self.resized.emit(self.size)
        self.surface = pygame.display.set_mode(size)
        self._size = size

    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, title: str):
        if title == self._title:
            return
        pygame.display.set_caption(title)
        self._title = title

    async def render(self, tick: Tick) -> None:
        """Render all sprites to the window surface.

        Args:
            tick (Tick): The current tick information.
        """
        self.surface.fill(pygame.Color(0, 0, 0))
        for z_index in sorted(sprites.layers.keys()):
            layer = sprites.layers[z_index]
            for sprite in layer:
                await sprite.update(tick)
                sprite.draw(self.surface)

    def flip(self) -> None:
        """Update the full display surface to the screen.
        """
        pygame.display.flip()
