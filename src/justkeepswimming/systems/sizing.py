from pygame import Rect, Surface, Vector2

from justkeepswimming.components.pseudo import ScenePseudoComponent, WindowPseudoComponent
from justkeepswimming.components.render import Renderer
from justkeepswimming.components.sizing import (
    AspectRatioConstraint,
    SceneSizeConstraint,
    ScreenSizeConstraint,
)
from justkeepswimming.components.physics import Transform
from justkeepswimming.ecs import SceneContext, System
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.systems.render import RenderSystem
from justkeepswimming.utilities.context import GameContext

class SceneSizeConstraintSystem(System):
    reads = frozenset({Transform})
    writes = frozenset({ScenePseudoComponent})
    before = frozenset({RenderSystem})
    after = frozenset({})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        surface = scene_context.surface
        for _, (transform, _) in scene_context.query(Transform, SceneSizeConstraint):
            transform.size = Vector2(surface.get_size())


class RendererTransformConstraintSystem(System):
    reads = frozenset({Transform, Renderer})
    writes = frozenset({Renderer})
    before = frozenset({RenderSystem})
    after = frozenset({})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        for _, (transform, renderer) in scene_context.query(
            Transform, Renderer
        ):
            if transform.size != Vector2(renderer.surface.get_size()):
                surface = Surface(
                    transform.size, flags=renderer.surface.get_flags()
                )
                destination = (
                    Vector2(surface.get_size()) / 2
                    - transform.size.elementwise() * transform.anchor
                )
                surface.blit(
                    renderer.surface,
                    destination,
                    area=Rect((0, 0), transform.size),
                )
                renderer.surface = surface


class AspectRatioConstraintSystem(System):
    reads = frozenset({Transform, AspectRatioConstraint})
    writes = frozenset({Transform})
    before = frozenset({})
    after = frozenset({})

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
    reads = frozenset({Transform, WindowPseudoComponent})
    writes = frozenset({Transform})
    before = frozenset({})
    after = frozenset({})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        window = engine_context.window
        for _, (transform, _) in scene_context.query(Transform, ScreenSizeConstraint):
            transform.size = window.size
