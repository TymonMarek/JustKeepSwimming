from dataclasses import dataclass, field

from pygame import Color, Surface

from justkeepswimming.ecs import Component
from justkeepswimming.utilities.image import Image


@dataclass
class MainCameraComponent(Component): ...


@dataclass
class CameraComponent(Component):
    surface: Surface = field(default_factory=lambda: Surface((0, 0)))


@dataclass
class RendererComponent(Component):
    surface: Surface = field(default_factory=lambda: Surface((0, 0)))
    background: Color = field(default_factory=lambda: Color(0, 0, 0, 0))


class SpriteComponent(Component):
    texture: Image
