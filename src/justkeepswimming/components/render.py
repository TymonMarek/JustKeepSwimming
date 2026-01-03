from dataclasses import dataclass, field

from pygame import Color, Font, Surface

from justkeepswimming.ecs import Component


@dataclass
class MainCamera(Component): ...


@dataclass
class Camera(Component):
    surface: Surface = field(default_factory=lambda: Surface((0, 0)))


@dataclass
class TextRenderer(Component):
    text: str
    font: Font
    color: Color
