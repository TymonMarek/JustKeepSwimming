from dataclasses import dataclass

from pygame import Color, Font

from src.ecs import Component

@dataclass
class MainCamera(Component): ...

@dataclass
class Camera(Component): ...


@dataclass
class TextRenderer(Component):
    text: str
    font: Font
    color: Color
