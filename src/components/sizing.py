from dataclasses import dataclass

from src.ecs import Component

@dataclass
class SceneSizeConstraint(Component): ...

@dataclass
class AspectRatioConstraint(Component):
    aspect_ratio: float


@dataclass
class ScreenSizeConstraint(Component): ...
