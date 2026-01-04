import pygame
from pygame import Color, Rect, Vector2

from justkeepswimming.components.physics import TransformComponent
from justkeepswimming.components.pseudo import (
    ScenePseudoComponent,
    WindowPseudoComponent,
)
from justkeepswimming.components.render import CameraComponent, MainCameraComponent
from justkeepswimming.ecs import Processor, SceneContext
from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.context import EngineContext


class CameraProcessor(Processor):
    reads = frozenset({TransformComponent, ScenePseudoComponent})
    writes = frozenset({CameraComponent, WindowPseudoComponent})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: EngineContext,
    ) -> None:
        for _, (camera, transform) in scene_context.query(
            CameraComponent, TransformComponent
        ):
            camera.surface = scene_context.surface.subsurface(
                Rect(transform.position, transform.size)
            )
        result = scene_context.query_one(
            CameraComponent, TransformComponent, MainCameraComponent
        )
        if result is not None:
            _, (camera, transform, _) = result
            window = engine_context.window
            camera_width, camera_height = camera.surface.get_size()
            window_width, window_height = window.surface.get_size()

            scale = min(window_width / camera_width, window_height / camera_height)
            new_width = int(camera_width * scale)
            new_height = int(camera_height * scale)

            scaled_surface = pygame.transform.smoothscale(
                camera.surface, Vector2(new_width, new_height)
            )

            x = (window_width - new_width) // 2
            y = (window_height - new_height) // 2
            window.surface.fill(Color(0, 0, 0))
            window.surface.blit(scaled_surface, Vector2(x, y))
            window.refresh()
