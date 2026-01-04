from pygame import Color

from justkeepswimming.components.physics import Transform
from justkeepswimming.components.pseudo import ScenePseudoComponent
from justkeepswimming.components.render import Renderer
from justkeepswimming.ecs import SceneContext, System
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.utilities.context import GameContext


BACKGROUND_COLOR: Color = Color(0, 0, 0)


class RenderSystem(System):
    reads = frozenset({Transform, Renderer})
    writes = frozenset({Renderer, ScenePseudoComponent})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        scene = scene_context.surface
        scene.fill(BACKGROUND_COLOR)
        for _, (transform, renderer) in scene_context.query(Transform, Renderer):
            if renderer.surface:
                scene.blit(
                    renderer.surface,
                    transform.position.elementwise() - transform.size.elementwise() * transform.anchor,
                )
