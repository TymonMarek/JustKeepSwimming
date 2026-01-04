from dataclasses import dataclass

from justkeepswimming.ecs import Component


@dataclass
class SurfaceTransformConstraintComponent(Component): ...


@dataclass
class SceneSizeConstraintComponent(Component): ...


@dataclass
class AspectRatioConstraintComponent(Component):
    aspect_ratio: float


@dataclass
class ScreenSizeConstraintComponent(Component): ...
