from dataclasses import dataclass, field

from justkeepswimming.ecs import Component
from justkeepswimming.utilities.animation import (
    Animation,
    AnimationTrack,
    AnimationType,
    Animator,
)


@dataclass
class AnimationComponent(Component):
    animation: Animation


@dataclass
class SpritesheetComponent(Component):
    animations: dict[AnimationType, Animation]


@dataclass
class AnimatorComponent(Component):
    animator: Animator = field(default_factory=Animator)


@dataclass
class AnimationStateComponent(Component):
    current_state: AnimationType = AnimationType.IDLE
    current_track: AnimationTrack | None = None
    current_speed: float = 1.0
