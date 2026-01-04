from dataclasses import dataclass, field

from pygame import Color, Surface

from justkeepswimming.ecs import Component
from justkeepswimming.utilities.image import Image


@dataclass
class MainCamera(Component): ...

@dataclass
class Camera(Component):
    surface: Surface = field(default_factory=lambda: Surface((0, 0)))


@dataclass
class Renderer(Component):
    surface: Surface = field(default_factory=lambda: Surface((0, 0)))
    background: Color = field(default_factory=lambda: Color(0, 0, 0, 0))


class Sprite(Component):
    texture: Image