from dataclasses import dataclass

from justkeepswimming.ecs import Component


@dataclass
class SurfaceTransformConstraintComponent(Component):
    pass


@dataclass
class SceneSizeConstraintComponent(Component):
    pass


@dataclass
class AspectRatioConstraintComponent(Component):
    aspect_ratio: float


@dataclass
class ScreenSizeConstraintComponent(Component):
    pass
