from pygame import Rect, Surface, Vector2

from justkeepswimming.components.physics import TransformComponent
from justkeepswimming.components.pseudo import (
    ScenePseudoComponent,
    WindowPseudoComponent,
)
from justkeepswimming.components.render import RendererComponent
from justkeepswimming.components.sizing import (
    AspectRatioConstraintComponent,
    SceneSizeConstraintComponent,
    ScreenSizeConstraintComponent,
)
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.processors.render import RendererProcessor
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.context import EngineContext


class SceneSizeConstraintProcessor(Processor):
    reads = frozenset({TransformComponent})
    writes = frozenset({ScenePseudoComponent})
    before = frozenset({RendererProcessor})
    after = frozenset({})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        surface = scene_context.surface
        for _, (transform, _) in scene_context.query(
            TransformComponent, SceneSizeConstraintComponent
        ):
            transform.size = Vector2(surface.get_size())


class RendererTransformConstraintProcessor(Processor):
    reads = frozenset({TransformComponent, RendererComponent})
    writes = frozenset({RendererComponent})
    before = frozenset({RendererProcessor})
    after = frozenset({})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (transform, renderer) in scene_context.query(
            TransformComponent, RendererComponent
        ):
            if transform.size != Vector2(renderer.surface.get_size()):
                surface = Surface(transform.size, flags=renderer.surface.get_flags())
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


class AspectRatioConstraintProcessor(Processor):
    reads = frozenset({TransformComponent, AspectRatioConstraintComponent})
    writes = frozenset({TransformComponent})
    before = frozenset({})
    after = frozenset({})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (transform, aspect_ratio_constraint) in scene_context.query(
            TransformComponent, AspectRatioConstraintComponent
        ):
            width, height = transform.size
            target_aspect_ratio = aspect_ratio_constraint.aspect_ratio

            current_aspect_ratio = width / height if height != 0 else 0

            if current_aspect_ratio > target_aspect_ratio:
                width = height * target_aspect_ratio
            else:
                height = width / target_aspect_ratio

            transform.size = Vector2(width, height)


class ScreenSizeConstraintProcessor(Processor):
    reads = frozenset({TransformComponent, WindowPseudoComponent})
    writes = frozenset({TransformComponent})
    before = frozenset({})
    after = frozenset({})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        window = engine_context.window
        for _, (transform, _) in scene_context.query(
            TransformComponent, ScreenSizeConstraintComponent
        ):
            transform.size = window.size
