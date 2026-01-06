import pygame
from pygame import Color

from justkeepswimming.components.physics import TransformComponent
from justkeepswimming.components.pseudo import ScenePseudoComponent
from justkeepswimming.components.render import RendererComponent
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.context import EngineContext

BACKGROUND_COLOR: Color = Color(0, 0, 0)


class RendererProcessor(Processor):
    reads = frozenset({TransformComponent, RendererComponent})
    writes = frozenset({RendererComponent, ScenePseudoComponent})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        scene = scene_context.surface
        scene.fill(BACKGROUND_COLOR)
        for _, (transform, renderer) in scene_context.query(
            TransformComponent, RendererComponent
        ):
            rotated_surface = pygame.transform.rotate(
                renderer.surface, -transform.rotation
            )
            rotated_rect = rotated_surface.get_rect()
            anchor_offset = transform.size.elementwise() * transform.anchor
            rotated_rect.center = transform.position - anchor_offset
            scene.blit(rotated_surface, rotated_rect.topleft)


class RendererPreProcessor(Processor):
    reads = frozenset({})
    writes = frozenset({RendererComponent})
    before = frozenset({RendererProcessor})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (renderer,) in scene_context.query(RendererComponent):
            renderer.surface.fill(Color(0, 0, 0, 0))
