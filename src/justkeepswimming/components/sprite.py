from dataclasses import dataclass

from justkeepswimming.ecs import Component
from justkeepswimming.utilities.image import Image


@dataclass
class SpriteComponent(Component):
    content: Image | None = None
