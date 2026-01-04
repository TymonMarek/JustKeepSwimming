from dataclasses import dataclass

from justkeepswimming.ecs import Component

@dataclass
class SurfaceTransformConstraint(Component): ...

@dataclass
class SceneSizeConstraint(Component): ...

@dataclass
class AspectRatioConstraint(Component):
    aspect_ratio: float


@dataclass
class ScreenSizeConstraint(Component): ...
