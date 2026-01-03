from pygame import Vector2

from justkeepswimming.components.sizing import AspectRatioConstraint, SceneSizeConstraint, ScreenSizeConstraint
from justkeepswimming.components.physics import Transform
from justkeepswimming.ecs import SceneContext, System
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.utilities.context import GameContext

class SceneSizeConstraintSystem(System):
    writes = frozenset({Transform})
    
    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        surface = scene_context.surface
        for _, (transform, _) in scene_context.query(Transform, SceneSizeConstraint):
            transform.size = Vector2(surface.get_size())


class AspectRatioConstraintSystem(System):
    reads = frozenset({Transform, AspectRatioConstraint})
    writes = frozenset({Transform})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        for _, (transform, aspect_ratio_constraint) in scene_context.query(
            Transform, AspectRatioConstraint
        ):
            width, height = transform.size
            target_aspect_ratio = aspect_ratio_constraint.aspect_ratio

            current_aspect_ratio = width / height if height != 0 else 0

            if current_aspect_ratio > target_aspect_ratio:
                width = height * target_aspect_ratio
            else:
                height = width / target_aspect_ratio

            transform.size = Vector2(width, height)


class ScreenSizeConstraintSystem(System):
    reads = frozenset({Transform, ScreenSizeConstraint})
    writes = frozenset({Transform})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        window = engine_context.window
        for _, (transform, _) in scene_context.query(Transform, ScreenSizeConstraint):
            transform.size = window.size
