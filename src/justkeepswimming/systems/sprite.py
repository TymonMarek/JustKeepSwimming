from pygame import Surface, Vector2
import pygame

from justkeepswimming.components.render import Renderer
from justkeepswimming.components.sprite import SpriteComponent
from justkeepswimming.ecs import SceneContext, System
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.systems.render import RenderSystem
from justkeepswimming.systems.sizing import RendererTransformConstraintSystem
from justkeepswimming.utilities.context import GameContext

index = 0

class SpriteSystem(System):
    reads = frozenset({SpriteComponent})
    writes = frozenset({Renderer})
    before = frozenset({RenderSystem})
    after = frozenset({RendererTransformConstraintSystem})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        for _, (sprite, renderer) in scene_context.query(
            SpriteComponent, Renderer
        ):
            surface = sprite.content if isinstance(sprite.content, Surface) else sprite.content.surface
            renderer.surface.blit(pygame.transform.scale(surface, renderer.surface.get_size()), Vector2(0, 0))