from typing import DefaultDict, List

from pygame import Surface, Vector2
import pygame

from clock import Tick

# A dictionary mapping z-index to a list of sprites at that z-index
layers: DefaultDict[int, List["Sprite"]] = DefaultDict(list)

pygame.display.init()

class Sprite:
    """An object that will be drawn to the screen. The contents of `Sprite.surface` will be drawn at `Sprite.position` on the target surface provided in `Sprite.draw()`.
    """
    def __init__(self) -> None:
        self._size = Vector2(0, 0)
        self.position = Vector2(0, 0)
        self.surface = Surface(self.size)
        self._z_index: int = 0
        self.__post_init__()

    def __post_init__(self) -> None:
        layer = layers[self.z_index]
        layer.append(self)

    def update(self, tick: Tick):
        """A function that fires at every tick. Should only be used when the sprite is animated or modified.

        Args:
            tick (`Tick`): The current tick information.
        """
        ...

    @property
    def z_index(self) -> int:
        return self._z_index
    
    @z_index.setter
    def z_index(self, new_z_index: int):
        if self._z_index == new_z_index:
            return 
        current_layer = layers[self._z_index]
        if self in current_layer:
            current_layer.remove(self)
        self._z_index = new_z_index   
        new_layer = layers[new_z_index]
        new_layer.append(self)

    @property
    def size(self) -> Vector2:
        return self._size
    
    @size.setter
    def size(self, new_size: Vector2):
        if new_size == self._size:
            return
        self._size = new_size
        self.surface = pygame.transform.scale(self.surface, self._size)

    def draw(self, target: Surface) -> None:
        """Draws the contents of `Sprite.surface` to the `target` surface at `Sprite.position`.

        Args:
            target (`pygame.Surface`): The surface to draw to.
        """
        target.blit(self.surface, self.position)