import pygame

class Window:
    def __init__(self) -> None:
        self.surface = pygame.display.set_mode()
        self._title = pygame.display.get_caption()[0]
        self._size = pygame.Vector2()

    @property
    def size(self) -> pygame.Vector2:
        return self._size
    
    @size.setter
    def size(self, size: pygame.Vector2):
        if size == self._size:
            return
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

    def flip(self) -> None:
        pygame.display.flip()
