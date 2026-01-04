from dataclasses import dataclass

from pygame import Surface

from justkeepswimming.ecs import Component
from justkeepswimming.utilities.image import Image


@dataclass
class SpriteComponent(Component):
    content: Image | Surface 
