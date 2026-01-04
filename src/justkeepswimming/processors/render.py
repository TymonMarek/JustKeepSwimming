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
            if renderer.surface:
                scene.blit(
                    renderer.surface,
                    transform.position.elementwise()
                    - transform.size.elementwise() * transform.anchor,
                )
