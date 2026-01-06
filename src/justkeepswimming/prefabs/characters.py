from justkeepswimming.components.animation import (
    AnimationStateComponent,
    AnimatorComponent,
    SpritesheetComponent,
)
from justkeepswimming.prefabs.renderable import RenderablePrefab
from justkeepswimming.processors.animation import (
    AnimationTrackPlaybackProcessor,
    CharacterAnimationProcessor,
    CharacterAnimationStateProcessors,
)
from justkeepswimming.utilities.prefab import Prefab


class CharacterPrefab(Prefab):
    extends = RenderablePrefab()
    components = [
        AnimatorComponent(),
        AnimationStateComponent(),
        SpritesheetComponent({}),
    ]
    processors = [
        AnimationTrackPlaybackProcessor,
        CharacterAnimationStateProcessors,
        CharacterAnimationProcessor,
    ]
