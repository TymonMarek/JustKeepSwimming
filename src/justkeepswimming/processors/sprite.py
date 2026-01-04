import pygame
from pygame import Surface, Vector2

from justkeepswimming.components.render import RendererComponent
from justkeepswimming.components.sprite import SpriteComponent
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.processors.render import RendererProcessor
from justkeepswimming.processors.sizing import RendererTransformConstraintProcessor
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.context import EngineContext

index = 0


class SpriteProcessor(Processor):
    reads = frozenset({SpriteComponent})
    writes = frozenset({RendererComponent})
    before = frozenset({RendererProcessor})
    after = frozenset({RendererTransformConstraintProcessor})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (sprite, renderer) in scene_context.query(
            SpriteComponent, RendererComponent
        ):
            surface = (
                sprite.content
                if isinstance(sprite.content, Surface)
                else sprite.content.surface
            )
            renderer.surface.blit(
                pygame.transform.scale(surface, renderer.surface.get_size()),
                Vector2(0, 0),
            )
