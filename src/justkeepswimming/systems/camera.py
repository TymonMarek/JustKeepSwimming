from pygame import Color, Rect, Vector2
import pygame

from justkeepswimming.components.pseudo import ScenePseudoComponent, WindowPseudoComponent
from justkeepswimming.ecs import SceneContext
from justkeepswimming.modules.clock import TickContext
from justkeepswimming.components.physics import Transform
from justkeepswimming.components.render import Camera, MainCamera

from justkeepswimming.ecs import System
from justkeepswimming.utilities.context import GameContext


class CameraSystem(System):
    reads = frozenset({Transform, ScenePseudoComponent})
    writes = frozenset({Camera, WindowPseudoComponent})

    async def update(
        self,
        tick_context: TickContext,
        scene_context: SceneContext,
        engine_context: GameContext,
    ) -> None:
        for _, (camera, transform) in scene_context.query(Camera, Transform):
            camera.surface = scene_context.surface.subsurface(
                Rect(transform.position, transform.size)
            )
        result = scene_context.query_one(Camera, Transform, MainCamera)
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
